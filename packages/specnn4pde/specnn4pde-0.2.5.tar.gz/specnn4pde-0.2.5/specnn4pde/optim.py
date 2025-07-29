__all__ = ['ARSAV', 'NAG_ARSAV', 'NAdam_RSAV', 'NAdam_ERSAV']

"""
sav.py

This module provides optimizers based on the Scalar Auxilary Variable (SAV) method.

Reference:
1. Liu, X.; Shen, J.; Zhang, X. 
    An Efficient and Robust SAV Based Algorithm for Discrete Gradient Systems Arising from Optimizations. 
    arXiv May 10, 2023. http://arxiv.org/abs/2301.02942
2. Zhang, S.; Zhang, J.; Shen, J.; Lin, G. 
    An Element-Wise RSAV Algorithm for Unconstrained Optimization Problems. 
    arXiv Sep. 7, 2023. http://arxiv.org/abs/2309.04013
3. Ma, Z.; Mao, Z.; Shen, J. 
    Efficient and Stable SAV-Based Methods for Gradient Flows Arising from Deep Learning. 
    JCP 2024. https://doi.org/10.1016/j.jcp.2024.112911
"""

from typing import List, Optional, Union, Tuple
import numpy as np
from autograd import grad, hessian
import sympy as sp

import torch
from torch import Tensor
from torch.optim import Optimizer

class ARSAV(Optimizer):
    r"""Implements Adaptive Relaxed Scalar Auxiliary Variable (ARSAV) algorithm.

    ..math::
        \begin{aligned}
            &\textbf { The adaptive RASV Scheme }\\[-1.ex]
            &\rule{110mm}{0.4pt}\\[-1.ex]
            &\textbf { input : } \delta t_0: \text { initial step-size, } \delta t_{\min }: \text { lower bound of step-size, }\\
            &\hspace{40pt} C: \text { constant to guarantee the positivity of } f(x)+C,\\
            &\hspace{40pt} \mathcal{L}: \text { the linear operator, } A=I+\delta t \mathcal{L},\\
            &\hspace{40pt} \theta_0: \text { initial parameter vector, }\\
            &\hspace{40pt} \eta: \text { relaxation constant which is less than } 1,\\
            &\hspace{40pt} \rho: \text { adaptive constant which is greater than } 1,\\
            &\hspace{40pt} \gamma: \text { threshold for the adaptive indicator } I(r, \theta).\\
            &\textbf { initialize : } r_0 \leftarrow \sqrt{f\left(\theta_0\right)+C}\\[-1.ex]
            &\rule{110mm}{0.4pt}\\[-1.ex]
            &\textbf { for } k=0,1,2, \ldots, M-1 \textbf { do }\\
            &\hspace{5mm}\textbf { if } \frac{r_k}{\sqrt{f\left(\theta_k\right)+C}}<\gamma \text { and } \delta t>\delta t_{\text {min }} \textbf { then }\\
            &\hspace{10mm} \delta t_{k+1}=\max \left\{\frac{r_k}{\sqrt{f\left(\theta_k\right)+C}} \delta t_k, \delta t_{\min }\right\}\\
            &\hspace{5mm}\textbf { else }\\
            &\hspace{10mm}\delta t_{k+1}=\rho \delta t_k\\
            &\hspace{5mm}g_k=\frac{\nabla f\left(\theta_k\right)}{\sqrt{f\left(\theta_k\right)+C}}\\
            &\hspace{5mm}\hat{g}_k=A^{-1} g_k\\
            &\hspace{5mm}\tilde{r}_{k+1}=\frac{r_k}{1+\frac{\delta t_{k+1}}{2}\left(g_k, \hat{g}_k\right)}\\
            &\hspace{5mm}\theta_{k+1}=\theta_k-\delta t_{k+1} \tilde{r}_{k+1} \hat{g}_k\\
            &\hspace{5mm}\xi=\frac{\sqrt{f\left(\theta_{k+1}\right)+C}-\sqrt{(1-\eta) \tilde{r}_{k+1}^2+\eta r_k^2+
                (1-\eta)\left(\tilde{r}_{k+1}-r_k\right)^2}}{\sqrt{f\left(\theta_{k+1}\right)+C}-\tilde{r}_{k+1}}\\
            &\hspace{5mm}\xi=\max \{0, \xi\}\\
            &\hspace{5mm}r_{k+1}=\xi \tilde{r}_{k+1}+(1-\xi) \sqrt{f\left(\theta_{k+1}\right)+C}\\
            &\rule{110mm}{0.4pt}\\[-1.ex]
            &\textbf { return } \theta_{\mathrm{M}}\\[-1.ex]
            &\rule{110mm}{0.4pt}\\[-1.ex]
        \end{aligned}

    For further details regarding the algorithm we refer to
        Liu, X.; Shen, J.; Zhang, X. 
        An Efficient and Robust SAV Based Algorithm for Discrete Gradient Systems Arising from Optimizations. 
        arXiv May 10, 2023. http://arxiv.org/abs/2301.02942

    Args:
    ----------
        params (iterable): iterable of parameters to optimize or dicts defining parameter groups
        init_loss (Tensor): initial loss value
        lr (float): initial step-size
        lr_min (float, optional): lower bound of step-size (default: 0.01)
        C (float, optional): constant to guarantee the positivity of f(x)+C (default: 0)
        opL (str, optional): linear operator for stabilization (default: 'trivial')
                             options: 'trivial': zero operator, 'diag_hessian': diagonal of Hessian matrix of f(x)
        eta (float, optional): relaxation constant (default: 0.99)
        rho (float, optional): adaptive constant which is greater than 1 (default: 1.1)
        gamma (float, optional): threshold for the adaptive indicator (default: 0.9)
        adaptive (bool, optional): whether to use adaptive step-size (default: True)
    """

    def __init__(self,
                 params, 
                 init_loss: Tensor, 
                 lr: float, 
                 lr_min: float = 0.01, 
                 C: float = 0, 
                 opL: str = 'trivial', 
                 eta: float = 0.99, 
                 rho: float = 1.1, 
                 gamma: float = 0.9, 
                 adaptive: bool = True,
                ):
        
        modified_energy = torch.sqrt(init_loss + C)
        defaults = dict(r=modified_energy, ME=modified_energy, lr=lr, lr_min=lr_min, C=C, opL=opL, 
                        eta=eta, rho=rho, gamma=gamma, adaptive=adaptive)
        super(ARSAV, self).__init__(params, defaults)
        self.loss = init_loss

    def step(self, closure = None) -> float:
        """Performs a single optimization step.

        Args:
        ----------
            closure (callable, optional): A closure that reevaluates the model and returns the loss.
            
        Returns:
        ----------
            float: The current loss value after the optimization step.
        """
        for group in self.param_groups:
            # adaptive step size according to the modified energy
            indicator = group['r'] / group['ME']
            if not group['adaptive']:
                pass
            elif indicator < group['gamma'] and group['lr'] > group['lr_min']:
                group['lr'] = max(indicator * group['lr'], group['lr_min'])
            else:
                group['lr'] = group['rho'] * group['lr']
           
            # set the operator L
            if group['opL'] == "trivial":
                # flatten the group parameters and gradients
                self.loss.backward()
                r_tilde = sum([p.grad.norm()**2 for p in group['params']]) / (group['ME']**2)
                r_tilde = group['r'] / (1 + group['lr'] * r_tilde / 2)
                for p in group['params']:
                    p.data -= group['lr'] * r_tilde * p.grad / group['ME']
            elif group['opL'] == "diag_hessian":
                # flatten the group parameters and gradients
                params_flatten = torch.cat([p.view(-1) for p in group['params']])
                grad1 = torch.autograd.grad(self.loss, group['params'], create_graph=True)
                grad_flatten = torch.cat([p.view(-1) for p in grad1])
                grad2 = []
                # calculate the diagonal of Hessian matrix
                # here we've calculate the whole Hessian matrix
                # TODO: calculate the diagonal of Hessian matrix without calculating the whole Hessian matrix
                for (g, x) in zip(grad1, group['params']):
                    hessian = torch.zeros_like(x)
                    for index in np.ndindex(*g.shape):
                        hessian[index] = (torch.autograd.grad(g[index], x, retain_graph=True)[0][index])
                    grad2.append(hessian.detach_())
                diag_L = torch.cat([p.view(-1) for p in grad2])
                # update params
                g = grad_flatten / group['ME']
                hat_g = (1 / (group['lr'] * diag_L + 1)) * g
                r_tilde = group['r'] / (1 + group['lr'] * torch.dot(g, hat_g) / 2)
                params_flatten = params_flatten - group['lr'] * r_tilde * hat_g

                # update group['params']
                start = 0
                for p in group['params']:
                    end = start + p.numel()
                    p.data = params_flatten[start:end].view(p.shape)
                    start = end
            else:
                raise ValueError("Invalid linear operator `opL`. Choose 'trivial' or 'diag_hessian'.")

            # update modefied energy (ME) and scalar auxilary variable (r)
            self.loss = closure()
            group['ME'] = torch.sqrt(self.loss + group['C'])
            if group['ME'] != r_tilde:
                xi = (group['ME'] - torch.sqrt((1-group['eta']) * r_tilde**2 + group['eta'] * group['r']**2 
                                               + (1-group['eta']) * (r_tilde-group['r'])**2)) / (group['ME'] - r_tilde)
                xi = max(xi, 0)
            else:
                xi = 0
            group['r'] = xi * r_tilde + (1 - xi) * group['ME']
            
        return self.loss.item()
    



class NAG_ARSAV(Optimizer):
    fr"""Combines the Nesterov Accelerated Gradient (NAG) method with the
        Adaptive Relaxed Scalar Auxiliary Variable (ARSAV) algorithm.

    ..math::

    Args:
    ----------
        params (iterable): iterable of parameters to optimize or dicts defining parameter groups
        init_loss (Tensor): initial loss value
        lr (float): initial step-size
        lr_min (float, optional): lower bound of step-size (default: 0.01)
        opL (str, optional): linear operator for stabilization (default: 'trivial')
                             options: 'trivial': zero operator, 'diag_hessian': diagonal of Hessian matrix of f(x)
        nu (float, optional): relaxation constant which is less than 1 (default: 0.99)
        rho (float, optional): adaptive constant which is greater than 1 (default: 1.1)
        beta (float, optional): threshold for the adaptive indicator (default: 0.9)
        gamma (float, optional): moment running average coefficient (default: 0.8)
        adaptive (bool, optional): whether to use adaptive step-size (default: True)
        MSAV (bool, optional): whether to multiply momentum with the SAV indicator (default: False)
        ODE_eta (float, optional): the constant eta in the ODE system
                                   if None, it will be set as initial time step eta and fixed
                                   if 0, it will be set as eta_sym which will be adapted throughout the iterations
        ODE_type (str, optional): the type of ODE 'fix_eta' or 'taylor' (default: 'taylor').
        ME_type (str, optional): the type of ME (string), 'PD' or 'PID' (default: 'PD').
        capturable (bool, optional): not implemented yet.
        differentiable (bool, optional): not implemented yet.
    """

    def __init__(self,
                 params, 
                 lr: float, 
                 lr_min: float = 0.01, 
                 opL: str = 'trivial', 
                 nu: float = 0.99, 
                 rho: float = 1.1, 
                 beta: float = 0.9,
                 gamma: float = 0.8, 
                 adaptive: bool = True,
                 MSAV: bool = False,
                 ODE_eta: float = 0,
                 ODE_type: str = 'taylor',
                 ME_type: str = 'PD',
                 capturable: bool = False,
                 differentiable: bool = False,
                ):

        #################################################
        # build the symbolic expressions for update rules    
        eta_sym, gamma_sym = sp.symbols('eta gamma')

        if ODE_eta is None:
            eta_0 = lr
        elif ODE_eta == 0:
            eta_0 = eta_sym
        else:
            eta_0 = ODE_eta

        if ODE_type == 'taylor':
            a = 2*(1-gamma_sym)/eta_0/(1+gamma_sym)
            kp = 2/eta_0/(1+gamma_sym)
            kd = 2*gamma_sym/(1+gamma_sym)
        elif ODE_type == 'fix_eta':
            a = (1-gamma_sym)/eta_0/gamma_sym
            kp = 1/eta_0/gamma_sym
            kd = 1

        self.coef = {}
        if ME_type == 'PID':
            # factor_v = 1
            # factor_ME = 1
            factor_v = gamma_sym * eta_0 / (2 * gamma_sym**2 - gamma_sym + 1)
            factor_ME = 1
            # factor_v = eta_0 / gamma_sym
            # factor_ME = eta_0 * gamma_sym

            self.coef['ME_v'] = sp.lambdify((eta_sym, gamma_sym), sp.simplify(factor_ME / factor_v**2 / 2))
            self.coef['ME_f'] = sp.lambdify((eta_sym, gamma_sym), sp.simplify((kp - kd * a) * factor_ME))
            self.coef['K_v'] = sp.lambdify((eta_sym, gamma_sym), sp.simplify(eta_sym * a * factor_ME / factor_v**2))
            self.coef['K_g'] = sp.lambdify((eta_sym, gamma_sym), sp.simplify(eta_sym * (kp - kd * a) * kd * factor_ME))
        elif ME_type == 'PD':
            factor_v = eta_0 / gamma_sym
            factor_ME = eta_0 * gamma_sym

            self.coef['ME_v'] = sp.lambdify((eta_sym, gamma_sym), sp.simplify(factor_ME / factor_v**2 / 2))
            self.coef['ME_f'] = sp.lambdify((eta_sym, gamma_sym), sp.simplify((kp + kd * a) * factor_ME))
            self.coef['tmp_v'] = sp.lambdify((eta_sym, gamma_sym), sp.simplify(1 / factor_v * eta_sym))
            self.coef['tmp_g'] = sp.lambdify((eta_sym, gamma_sym), sp.simplify(-kd * eta_sym))
            self.coef['K_tmp'] = sp.lambdify((eta_sym, gamma_sym), sp.simplify(a * factor_ME / eta_sym))
            self.coef['K_g'] = sp.lambdify((eta_sym, gamma_sym), sp.simplify(eta_sym * kd * kp * factor_ME))

        self.coef['v_v'] = sp.lambdify((eta_sym, gamma_sym), sp.simplify(1 / (1 + eta_sym * a)))
        self.coef['v_g'] = sp.lambdify((eta_sym, gamma_sym), sp.simplify(-eta_sym * (kp - a * kd) * factor_v / (1 + eta_sym * a)))
        self.coef['theta_v'] = sp.lambdify((eta_sym, gamma_sym), sp.simplify(eta_sym / factor_v))
        self.coef['theta_g'] = sp.lambdify((eta_sym, gamma_sym), sp.simplify(-eta_sym * kd))
        #################################################

        defaults = dict(lr=lr, lr_min=lr_min, opL=opL, savs_history=[],
                        nu=nu, rho=rho, beta=beta, gamma=gamma, adaptive=adaptive, MSAV=MSAV, ME_type=ME_type,
                        capturable=capturable, differentiable=differentiable)
        super(NAG_ARSAV, self).__init__(params, defaults)


    def __setstate__(self, state):
        super().__setstate__(state)
        # code for checkpoint compatibility
        for group in self.param_groups:
            group.setdefault('capturable', False)
            group.setdefault('differentiable', False)
        state_values = list(self.state.values())
        step_is_tensor = (len(state_values) != 0) and torch.is_tensor(state_values[0]['step'])
        if not step_is_tensor:
            for s in state_values:
                s['step'] = torch.tensor(float(s['step']))

    def _init_group(self, group, params_with_grad, grads, exp_avgs, exp_avg_sqs, state_steps, 
                    loss, MEs, r_tildes, lrs, Ks):
        for p in group['params']:
            if p.grad is not None:
                params_with_grad.append(p)
                if p.grad.is_sparse:
                    raise RuntimeError('NAdam does not support sparse gradients')
                grads.append(p.grad)

                state = self.state[p]
                # Lazy state initialization
                if len(state) == 0:
                    # note(crcrpar): [special device hosting for step]
                    # Deliberately host `step` and `mu_product` on CPU if capturable is False.
                    # This is because kernel launches are costly on CUDA and XLA.
                    state['step'] = (
                        torch.zeros((), dtype=torch.float, device=p.device)
                        if group['capturable'] else torch.tensor(0.)
                    )
                    # Exponential moving average of gradient values
                    state['exp_avg'] = torch.zeros_like(p, memory_format=torch.preserve_format)
                    # state['exp_avg'] = torch.clone(- float(group['lr']) * p).detach()
                    # Exponential moving average of squared gradient values
                    state['exp_avg_sq'] = torch.zeros_like(p, memory_format=torch.preserve_format)
                    # modified energy (ME) and scalar auxilary variable (r)
                    state['ME'] = self.coef['ME_f'](group['lr'], group['gamma']) * loss
                    state['r_tilde'] = state['ME'].clone()
                    state['lr'] = torch.tensor(float(group['lr']))
                    # state['lr'] = torch.tensor(group['lr'], dtype=p.dtype, device=p.device)
                    state['K'] = torch.zeros_like(loss, memory_format=torch.preserve_format)

                exp_avgs.append(state['exp_avg'])
                exp_avg_sqs.append(state['exp_avg_sq'])
                state_steps.append(state['step'])
                MEs.append(state['ME'])
                r_tildes.append(state['r_tilde'])
                lrs.append(state['lr'])
                Ks.append(state['K'])

    @torch.no_grad()
    def step(self, closure):
        """Performs a single optimization step.

        Args:
            closure (Callable): A closure that reevaluates the model
                and returns the loss.
        """
        self._cuda_graph_capture_health_check()

        # Make sure the closure is always called with grad enabled
        closure = torch.enable_grad()(closure)
        loss = closure()

        for group in self.param_groups:
            params_with_grad = []
            grads = []
            exp_avgs = []
            exp_avg_sqs = []
            state_steps = []
            MEs = []
            r_tildes = []
            lrs = []
            Ks = []

            self._init_group(group, params_with_grad, grads, exp_avgs, exp_avg_sqs, state_steps, 
                             loss, MEs, r_tildes, lrs, Ks)

            savs = _single_tensor_NAG_ARSAV(params_with_grad,
                                    grads,
                                    exp_avgs,
                                    exp_avg_sqs,
                                    state_steps,
                                    loss=loss,
                                    MEs=MEs,
                                    r_tildes=r_tildes,
                                    Ks=Ks,
                                    lrs=lrs,
                                    lr_min=group['lr_min'],
                                    opL=group['opL'],
                                    nu=group['nu'],
                                    rho=group['rho'],
                                    beta=group['beta'],
                                    gamma=group['gamma'],
                                    adaptive=group['adaptive'],
                                    MSAV=group['MSAV'],
                                    ME_type=group['ME_type'],
                                    coef=self.coef,
                                    capturable=group['capturable'],
                                    differentiable=group['differentiable'])
            group['savs_history'].append(savs)
            # TODO: _multi_tensor version is not implemented yet
        return loss




def _single_tensor_NAG_ARSAV(params: List[Tensor],
                             grads: List[Tensor],
                             exp_avgs: List[Tensor],
                             exp_avg_sqs: List[Tensor],
                             state_steps: List[Tensor],
                             loss: Optional[Tensor],
                             MEs: List[Tensor],
                             r_tildes: List[Tensor],
                             Ks: List[Tensor],
                             *,
                             lrs: List[float],
                             lr_min: float,
                             opL: str,
                             nu: float,
                             rho: float,
                             beta: float,
                             gamma: float,
                             adaptive: bool,
                             MSAV: bool,
                             ME_type: str,
                             coef: dict,
                             capturable: bool,
                             differentiable: bool):
    savs = []
    for i, param in enumerate(params):
        g = grads[i]
        v = exp_avgs[i]
        exp_avg_sq = exp_avg_sqs[i]
        step_t = state_steps[i]
        ME = MEs[i]
        r_tilde = r_tildes[i]
        lr = lrs[i]
        K = Ks[i]

        # If compiling, the compiler will handle cudagraph checks, see note [torch.compile x capturable]
        if capturable and not torch._utils.is_compiling():
            assert (
                (param.is_cuda and step_t.is_cuda) or (param.is_xla and step_t.is_xla)
            ), "If capturable=True, params and state_steps must be CUDA or XLA tensors."

        # update step
        step_t += 1

        if capturable:
            step = step_t
            ME_last = ME.clone()
        else:
            step = step_t.item()
            ME_last = ME.item()

        ME = float(coef['ME_v'](lr, gamma)) * torch.sum(v * v) + float(coef['ME_f'](lr, gamma)) * loss
        MEs[i].copy_(ME)

        if ME - r_tilde > r_tilde * K / ME_last:
            xi = 1 - (nu * r_tilde * K / ME_last / (ME - r_tilde)).item()
            xi = max(xi, 0)
        else:
            xi = 0
        r = xi * r_tilde + (1 - xi) * ME

        if adaptive:
            indicator = r / ME
            if indicator < beta and lr > lr_min:
                lr = max(indicator.item() * lr, torch.tensor(float(lr_min)))
            else:
                lr = rho * lr
        lrs[i].copy_(lr)
        # print(lrs[i])

        if ME_type == 'PID':
            K = float(coef['K_v'](lr, gamma))*torch.sum(v * v) + float(coef['K_g'](lr, gamma))*torch.sum(g * g)
        elif ME_type == 'PD':
            tmp = float(coef['tmp_v'](lr, gamma)) * v + float(coef['tmp_g'](lr, gamma)) * g
            K = float(coef['K_tmp'](lr, gamma))*torch.sum(tmp * tmp) + float(coef['K_g'](lr, gamma))*torch.sum(g * g)
        Ks[i].copy_(K)
        r_tilde = r / (1 + K / ME)
        r_tildes[i].copy_(r_tilde)
       
        m_indicator = (r / ME).item() if MSAV else 1
        v = m_indicator * float(coef['v_v'](lr, gamma)) * v + r_tilde / ME * float(coef['v_g'](lr, gamma)) * g
        exp_avgs[i].copy_(v)

        if opL == "trivial":
            update = float(coef['theta_v'](lr, gamma)) * v + r_tilde / ME * float(coef['theta_g'](lr, gamma)) * g
            param.add_(update)
        elif opL == "diag_hessian":
            # TODO: to be implemented
            pass
        else:
            raise ValueError("Invalid linear operator `opL`. Choose 'trivial' or 'diag_hessian'.")
        
        savs.append((r / ME).item())
    return savs





class NAG_ARSAV_batch(Optimizer):
    fr"""Combines the Nesterov Accelerated Gradient (NAG) method with the
        Adaptive Relaxed Scalar Auxiliary Variable (ARSAV) algorithm.

    ..math::

    Args:
    ----------
        params (iterable): iterable of parameters to optimize or dicts defining parameter groups
        init_loss (Tensor): initial loss value
        lr (float): initial step-size
        lr_min (float, optional): lower bound of step-size (default: 0.001)
        opL (str, optional): linear operator for stabilization (default: 'trivial')
                             options: 'trivial': zero operator, 'diag_hessian': diagonal of Hessian matrix of f(x)
        nu (float, optional): relaxation constant which is less than 1 (default: 0.999)
        rho (float, optional): adaptive constant which is greater than 1 (default: 1.1)
        beta (float, optional): threshold for the adaptive indicator (default: 0.9)
        gamma (float, optional): moment running average coefficient (default: 0.9)
        adaptive (bool, optional): whether to use adaptive step-size (default: True)
        MSAV (bool, optional): whether to multiply momentum with the SAV indicator (default: False)
        ODE_eta (float, optional): the constant eta in the ODE system
                                   if None, it will be set as initial time step eta and fixed
                                   if 0, it will be set as eta_sym which will be adapted throughout the iterations
        ODE_type (str, optional): the type of ODE 'fix_eta' or 'taylor' (default: 'fix_eta').
        ME_type (str, optional): the type of ME (string), 'PD' or 'PID' (default: 'PD').
        capturable (bool, optional): not implemented yet.
        differentiable (bool, optional): not implemented yet.
    """

    def __init__(self,
                 params, 
                 lr: float, 
                 lr_min: float = 0.001, 
                 opL: str = 'trivial', 
                 nu: float = 0.999, 
                 rho: float = 1.1, 
                 beta: float = 0.9,
                 gamma: float = 0.9, 
                 adaptive: bool = True,
                 MSAV: bool = False,
                 ODE_eta: float = 0,
                 ODE_type: str = 'fix_eta',
                 ME_type: str = 'PD',
                 capturable: bool = False,
                 differentiable: bool = False,
                ):

        #################################################
        # build the symbolic expressions for update rules    
        eta_sym, gamma_sym = sp.symbols('eta gamma')

        if ODE_eta is None:
            eta_0 = lr
        elif ODE_eta == 0:
            eta_0 = eta_sym
        else:
            eta_0 = ODE_eta

        if ODE_type == 'taylor':
            a = 2*(1-gamma_sym)/eta_0/(1+gamma_sym)
            kp = 2/eta_0/(1+gamma_sym)
            kd = 2*gamma_sym/(1+gamma_sym)
        elif ODE_type == 'fix_eta':
            a = (1-gamma_sym)/eta_0/gamma_sym
            kp = 1/eta_0/gamma_sym
            kd = 1

        self.coef = {}
        if ME_type == 'PID':
            # factor_v = 1
            # factor_ME = 1
            factor_v = gamma_sym * eta_0 / (2 * gamma_sym**2 - gamma_sym + 1)
            factor_ME = 1
            # factor_v = eta_0 / gamma_sym
            # factor_ME = eta_0 * gamma_sym

            self.coef['ME_v'] = sp.lambdify((eta_sym, gamma_sym), sp.simplify(factor_ME / factor_v**2 / 2))
            self.coef['ME_f'] = sp.lambdify((eta_sym, gamma_sym), sp.simplify((kp - kd * a) * factor_ME))
            self.coef['K_v'] = sp.lambdify((eta_sym, gamma_sym), sp.simplify(eta_sym * a * factor_ME / factor_v**2))
            self.coef['K_g'] = sp.lambdify((eta_sym, gamma_sym), sp.simplify(eta_sym * (kp - kd * a) * kd * factor_ME))
        elif ME_type == 'PD':
            factor_v = eta_0 / gamma_sym
            factor_ME = eta_0 * gamma_sym

            self.coef['ME_v'] = sp.lambdify((eta_sym, gamma_sym), sp.simplify(factor_ME / factor_v**2 / 2))
            self.coef['ME_f'] = sp.lambdify((eta_sym, gamma_sym), sp.simplify((kp + kd * a) * factor_ME))
            self.coef['tmp_v'] = sp.lambdify((eta_sym, gamma_sym), sp.simplify(1 / factor_v * eta_sym))
            self.coef['tmp_g'] = sp.lambdify((eta_sym, gamma_sym), sp.simplify(-kd * eta_sym))
            self.coef['K_tmp'] = sp.lambdify((eta_sym, gamma_sym), sp.simplify(a * factor_ME / eta_sym))
            self.coef['K_g'] = sp.lambdify((eta_sym, gamma_sym), sp.simplify(eta_sym * kd * kp * factor_ME))

        self.coef['v_v'] = sp.lambdify((eta_sym, gamma_sym), sp.simplify(1 / (1 + eta_sym * a)))
        self.coef['v_g'] = sp.lambdify((eta_sym, gamma_sym), sp.simplify(-eta_sym * (kp - a * kd) * factor_v / (1 + eta_sym * a)))
        self.coef['theta_v'] = sp.lambdify((eta_sym, gamma_sym), sp.simplify(eta_sym / factor_v))
        self.coef['theta_g'] = sp.lambdify((eta_sym, gamma_sym), sp.simplify(-eta_sym * kd))
        #################################################

        defaults = dict(lr=lr, lr_min=lr_min, opL=opL, savs_history=[],
                        nu=nu, rho=rho, beta=beta, gamma=gamma, adaptive=adaptive, MSAV=MSAV, ME_type=ME_type,
                        capturable=capturable, differentiable=differentiable)
        super(NAG_ARSAV_batch, self).__init__(params, defaults)


    def __setstate__(self, state):
        super().__setstate__(state)
        # code for checkpoint compatibility
        for group in self.param_groups:
            group.setdefault('capturable', False)
            group.setdefault('differentiable', False)
        state_values = list(self.state.values())
        step_is_tensor = (len(state_values) != 0) and torch.is_tensor(state_values[0]['step'])
        if not step_is_tensor:
            for s in state_values:
                s['step'] = torch.tensor(float(s['step']))

    def _init_group(self, group, params_with_grad, grads, exp_avgs, exp_avg_sqs, state_steps, 
                    epoch_delta_params, epoch_sum_exp_avgs, epoch_sum_losses,
                    loss, MEs, r_tildes, lrs, Ks):
        for p in group['params']:
            if p.grad is not None:
                params_with_grad.append(p)
                if p.grad.is_sparse:
                    raise RuntimeError('NAdam does not support sparse gradients')
                grads.append(p.grad)

                state = self.state[p]
                # Lazy state initialization
                if len(state) == 0:
                    # note(crcrpar): [special device hosting for step]
                    # Deliberately host `step` and `mu_product` on CPU if capturable is False.
                    # This is because kernel launches are costly on CUDA and XLA.
                    state['step'] = (
                        torch.zeros((), dtype=torch.float, device=p.device)
                        if group['capturable'] else torch.tensor(0.)
                    )
                    # Exponential moving average of gradient values
                    state['exp_avg'] = torch.zeros_like(p, memory_format=torch.preserve_format)
                    # Exponential moving average of squared gradient values
                    state['exp_avg_sq'] = torch.zeros_like(p, memory_format=torch.preserve_format)

                    # save the info of the epoch for SAV update
                    state['epoch_delta_param'] = torch.zeros_like(p, memory_format=torch.preserve_format)
                    state['epoch_sum_exp_avg'] = torch.zeros_like(p, memory_format=torch.preserve_format)
                    state['epoch_sum_loss'] = torch.zeros_like(loss, memory_format=torch.preserve_format)

                    # modified energy (ME) and scalar auxilary variable (r)
                    state['ME'] = torch.zeros_like(loss, memory_format=torch.preserve_format)   # if it converge to 0, may lead to error!!!!!!
                    state['r_tilde'] = torch.zeros_like(loss, memory_format=torch.preserve_format)
                    state['lr'] = torch.tensor(float(group['lr']))
                    # state['lr'] = torch.tensor(group['lr'], dtype=p.dtype, device=p.device)
                    state['K'] = torch.zeros_like(loss, memory_format=torch.preserve_format)

                exp_avgs.append(state['exp_avg'])
                exp_avg_sqs.append(state['exp_avg_sq'])
                state_steps.append(state['step'])
                epoch_delta_params.append(state['epoch_delta_param'])
                epoch_sum_exp_avgs.append(state['epoch_sum_exp_avg'])
                epoch_sum_losses.append(state['epoch_sum_loss'])
                MEs.append(state['ME'])
                r_tildes.append(state['r_tilde'])
                lrs.append(state['lr'])
                Ks.append(state['K'])

    @torch.no_grad()
    def step(self, closure, final_batch: bool = False):
        """Performs a single optimization step.

        Args:
            closure (Callable): A closure that reevaluates the model
                and returns the loss.
            final_batch (bool): If True, the step is performed at the end of an epoch,
                SAV will be updated with the current loss, and the history of SAVs will be cleared.
        """
        self._cuda_graph_capture_health_check()

        # Make sure the closure is always called with grad enabled
        closure = torch.enable_grad()(closure)
        loss = closure()

        for group in self.param_groups:
            params_with_grad = []
            grads = []
            exp_avgs = []
            exp_avg_sqs = []
            state_steps = []
            epoch_delta_params = []
            epoch_sum_exp_avgs = []
            epoch_sum_losses = []
            MEs = []
            r_tildes = []
            lrs = []
            Ks = []

            self._init_group(group, params_with_grad, grads, exp_avgs, exp_avg_sqs, state_steps, 
                             epoch_delta_params, epoch_sum_exp_avgs, epoch_sum_losses,
                             loss, MEs, r_tildes, lrs, Ks)

            _single_tensor_NAG_ARSAV_batch(params_with_grad,
                                    grads,
                                    exp_avgs,
                                    exp_avg_sqs,
                                    state_steps,
                                    epoch_delta_params=epoch_delta_params,
                                    epoch_sum_exp_avgs=epoch_sum_exp_avgs,
                                    epoch_sum_losses=epoch_sum_losses,
                                    loss=loss,
                                    MEs=MEs,
                                    r_tildes=r_tildes,
                                    Ks=Ks,
                                    lrs=lrs,
                                    lr_min=group['lr_min'],
                                    opL=group['opL'],
                                    nu=group['nu'],
                                    rho=group['rho'],
                                    beta=group['beta'],
                                    gamma=group['gamma'],
                                    adaptive=group['adaptive'],
                                    MSAV=group['MSAV'],
                                    ME_type=group['ME_type'],
                                    coef=self.coef,
                                    final_batch=final_batch,
                                    capturable=group['capturable'],
                                    differentiable=group['differentiable'])
            
            # TODO: _multi_tensor version is not implemented yet
        return loss





def _single_tensor_NAG_ARSAV_batch(params: List[Tensor],
                             grads: List[Tensor],
                             exp_avgs: List[Tensor],
                             exp_avg_sqs: List[Tensor],
                             state_steps: List[Tensor],
                             epoch_delta_params: List[Tensor],
                             epoch_sum_exp_avgs: List[Tensor],
                             epoch_sum_losses: List[Tensor],
                             loss: Optional[Tensor],
                             MEs: List[Tensor],
                             r_tildes: List[Tensor],
                             Ks: List[Tensor],
                             *,
                             lrs: List[float],
                             lr_min: float,
                             opL: str,
                             nu: float,
                             rho: float,
                             beta: float,
                             gamma: float,
                             adaptive: bool,
                             MSAV: bool,
                             ME_type: str,
                             coef: dict,
                             final_batch: bool = False,
                             capturable: bool,
                             differentiable: bool):
    # Apply NAG
    for i, param in enumerate(params):
        g = grads[i]
        v = exp_avgs[i]
        exp_avg_sq = exp_avg_sqs[i]
        step_t = state_steps[i]
        lr = lrs[i]

        # If compiling, the compiler will handle cudagraph checks, see note [torch.compile x capturable]
        if capturable and not torch._utils.is_compiling():
            assert (
                (param.is_cuda and step_t.is_cuda) or (param.is_xla and step_t.is_xla)
            ), "If capturable=True, params and state_steps must be CUDA or XLA tensors."

        # update step
        step_t += 1

        if capturable:
            step = step_t
        else:
            step = step_t.item()

        # NAG update   
        if (v == 0).all():
            v = torch.clone(-lr * g).detach()
        else:
            v = float(coef['v_v'](lr, gamma)) * v + float(coef['v_g'](lr, gamma)) * g
        exp_avgs[i].copy_(v)
        update = float(coef['theta_v'](lr, gamma)) * v + float(coef['theta_g'](lr, gamma)) * g
        # update = gamma * v - lr * g
        param.add_(update)

        # Save info for SAV update
        dp = epoch_delta_params[i]
        sum_v = epoch_sum_exp_avgs[i]
        sum_loss = epoch_sum_losses[i]
        dp.add_(update)
        sum_v.add_(v)
        sum_loss += loss

        if final_batch:     # Apply SAV update at the end of the epoch
            ME = MEs[i]
            r_tilde = r_tildes[i]
            K = Ks[i]
            sum_g = (dp - gamma * sum_v) / lr

            if capturable:
                ME_last = ME.clone()
            else:
                ME_last = ME.item()

            ME = float(coef['ME_v'](lr, gamma)) * torch.sum(sum_v * sum_v) + float(coef['ME_f'](lr, gamma)) * sum_loss
            MEs[i].copy_(ME)

            if ME_type == 'PID':
                K = float(coef['K_v'](lr, gamma))*torch.sum(sum_v * sum_v) + float(coef['K_g'](lr, gamma))*torch.sum(sum_g * sum_g)
            elif ME_type == 'PD':
                K = float(coef['K_tmp'](lr, gamma))*torch.sum(dp * dp) + float(coef['K_g'](lr, gamma))*torch.sum(sum_g * sum_g)
            Ks[i].copy_(K)

            if r_tilde == 0:    # first SAV update
                r_tilde = torch.clone(ME).detach()

            if ME_last != 0 and (ME - r_tilde > r_tilde * K / ME_last):
                xi = 1 - (nu * r_tilde * K / ME_last / (ME - r_tilde)).item()
                xi = max(xi, 0)
            else:
                xi = 0
            r = xi * r_tilde + (1 - xi) * ME

            r_tilde = r / (1 + K / ME)
            r_tildes[i].copy_(r_tilde)   
               
            if adaptive:
                indicator = r / ME
                if indicator < beta and lr > lr_min:
                    lr = max(indicator.item() * lr, torch.tensor(float(lr_min)))
                else:
                    lr = rho * lr
            lrs[i].copy_(lr)

            if opL == "trivial":
                update = (r_tilde / ME - 1) * dp
                param.add_(update)
            elif opL == "diag_hessian":
                # TODO: to be implemented
                pass
            else:
                raise ValueError("Invalid linear operator `opL`. Choose 'trivial' or 'diag_hessian'.")

            dp.zero_()
            sum_v.zero_()
            sum_loss.zero_()




class NAdam_RSAV(Optimizer):
    fr"""Combines the NAdam method with the
        Relaxed Scalar Auxiliary Variable (RSAV) algorithm.

    ..math::

    Args:
    ----------
        params (iterable): iterable of parameters to optimize or dicts defining parameter groups
        init_loss (Tensor): initial loss value
        lr (float): initial step-size
        lr_min (float, optional): not used, kept for compatibility
                                  lower bound of step-size (default: 0.01)
        opL (str, optional): linear operator for stabilization (default: 'trivial')
                             options: 'trivial': zero operator, 'diag_hessian': diagonal of Hessian matrix of f(x)
        nu (float, optional): relaxation constant which is less than 1 (default: 0.99)
        beta1 (float, optional): coefficients used for computing running averages of gradient (default: 0.9)
        beta2 (float, optional): coefficients used for computing running averages of squared gradient (default: 0.999)
        eps (float, optional): term added to the denominator to improve numerical stability (default: 1e-8)
        adaptive (bool, optional): whether to use adaptive step-size (default: True)
        MSAV (bool, optional): whether to multiply momentum with the SAV indicator (default: False)
        capturable (bool, optional): not implemented yet.
        differentiable (bool, optional): not implemented yet.
    """

    def __init__(self,
                 params, 
                 lr: float, 
                 lr_min: float = 0.01, 
                 opL: str = 'trivial', 
                 nu: float = 0.99, 
                 beta1: float = 0.9,
                 beta2: float = 0.999,
                 eps: float = 1e-8,
                 adaptive: bool = True,
                 MSAV: bool = False,
                 capturable: bool = False,
                 differentiable: bool = False,
                ):

        #################################################
        # build the symbolic expressions for update rules    
        self.coef = {}
        self.coef['ME_v'] = lambda eta, beta1: beta1**3 / 2 * eta
        self.coef['ME_f'] = lambda eta, beta1: 2 - beta1
        self.coef['tmp_v'] = lambda eta, beta1: eta * beta1
        self.coef['tmp_g'] = lambda eta, beta1: -eta
        self.coef['K_tmp'] = lambda eta, beta1: (1 - beta1) / eta
        self.coef['K_g'] = lambda eta, beta1: eta

        self.coef['v_v'] = lambda eta, beta1: beta1
        self.coef['v_g'] = lambda eta, beta1: -1
        self.coef['theta_v'] = lambda eta, beta1: eta * beta1
        self.coef['theta_g'] = lambda eta, beta1: -eta
        #################################################

        defaults = dict(lr=lr, lr_min=lr_min, opL=opL, savs_history=[],
                        nu=nu, beta1=beta1, beta2=beta2, eps=eps, adaptive=adaptive, MSAV=MSAV,
                        capturable=capturable, differentiable=differentiable)
        super(NAdam_RSAV, self).__init__(params, defaults)


    def __setstate__(self, state):
        super().__setstate__(state)
        # code for checkpoint compatibility
        for group in self.param_groups:
            group.setdefault('capturable', False)
            group.setdefault('differentiable', False)
        state_values = list(self.state.values())
        step_is_tensor = (len(state_values) != 0) and torch.is_tensor(state_values[0]['step'])
        if not step_is_tensor:
            for s in state_values:
                s['step'] = torch.tensor(float(s['step']))

    def _init_group(self, group, params_with_grad, grads, exp_avgs, exp_avg_sqs, state_steps, 
                    loss, MEs, r_tildes, init_lrs, lrs, Ks):
        for p in group['params']:
            if p.grad is not None:
                params_with_grad.append(p)
                if p.grad.is_sparse:
                    raise RuntimeError('NAdam does not support sparse gradients')
                grads.append(p.grad)

                state = self.state[p]
                # Lazy state initialization
                if len(state) == 0:
                    # note(crcrpar): [special device hosting for step]
                    # Deliberately host `step` and `mu_product` on CPU if capturable is False.
                    # This is because kernel launches are costly on CUDA and XLA.
                    state['step'] = (
                        torch.zeros((), dtype=torch.float, device=p.device)
                        if group['capturable'] else torch.tensor(0.)
                    )
                    # Exponential moving average of gradient values
                    state['exp_avg'] = torch.zeros_like(p, memory_format=torch.preserve_format)
                    # Exponential moving average of squared gradient values
                    # state['exp_avg_sq'] = torch.zeros_like(p, memory_format=torch.preserve_format)
                    state['exp_avg_sq'] = torch.tensor(0, dtype=p.dtype, device=p.device)
                    # modified energy (ME) and scalar auxilary variable (r)
                    state['ME'] = self.coef['ME_f'](group['lr'], group['beta1']) * loss
                    state['r_tilde'] = state['ME'].clone()
                    # state['init_lr'] = torch.tensor(float(group['lr']))
                    # state['lr'] = torch.tensor(float(group['lr']))
                    state['init_lr'] = torch.tensor(group['lr'], dtype=p.dtype, device=p.device)
                    state['lr'] = torch.tensor(group['lr'], dtype=p.dtype, device=p.device)
                    state['K'] = torch.zeros_like(loss, memory_format=torch.preserve_format)

                exp_avgs.append(state['exp_avg'])
                exp_avg_sqs.append(state['exp_avg_sq'])
                state_steps.append(state['step'])
                MEs.append(state['ME'])
                r_tildes.append(state['r_tilde'])
                init_lrs.append(state['init_lr'])
                lrs.append(state['lr'])
                Ks.append(state['K'])

    @torch.no_grad()
    def step(self, closure):
        """Performs a single optimization step.

        Args:
            closure (Callable): A closure that reevaluates the model
                and returns the loss.
        """
        self._cuda_graph_capture_health_check()

        # Make sure the closure is always called with grad enabled
        closure = torch.enable_grad()(closure)
        loss = closure()

        for group in self.param_groups:
            params_with_grad = []
            grads = []
            exp_avgs = []
            exp_avg_sqs = []
            state_steps = []
            MEs = []
            r_tildes = []
            init_lrs = []
            lrs = []
            Ks = []

            self._init_group(group, params_with_grad, grads, exp_avgs, exp_avg_sqs, state_steps, 
                             loss, MEs, r_tildes, init_lrs, lrs, Ks)

            savs = _single_tensor_NAdam_RSAV(params_with_grad,
                                    grads,
                                    exp_avgs,
                                    exp_avg_sqs,
                                    state_steps,
                                    loss=loss,
                                    MEs=MEs,
                                    r_tildes=r_tildes,
                                    Ks=Ks,
                                    init_lrs=init_lrs,
                                    lrs=lrs,
                                    lr_min=group['lr_min'],
                                    opL=group['opL'],
                                    nu=group['nu'],
                                    beta1=group['beta1'],
                                    beta2=group['beta2'],
                                    eps=group['eps'],
                                    adaptive=group['adaptive'],
                                    MSAV=group['MSAV'],
                                    coef=self.coef,
                                    capturable=group['capturable'],
                                    differentiable=group['differentiable'])
            group['savs_history'].append(savs)
            # TODO: _multi_tensor version is not implemented yet
        return loss




def _single_tensor_NAdam_RSAV(params: List[Tensor],
                             grads: List[Tensor],
                             exp_avgs: List[Tensor],
                             exp_avg_sqs: List[Tensor],
                             state_steps: List[Tensor],
                             loss: Optional[Tensor],
                             MEs: List[Tensor],
                             r_tildes: List[Tensor],
                             Ks: List[Tensor],
                             *,
                             init_lrs: List[float],
                             lrs: List[float],
                             lr_min: float,
                             opL: str,
                             nu: float,
                             beta1: float,
                             beta2: float,
                             eps: float,
                             adaptive: bool,
                             MSAV: bool,
                             coef: dict,
                             capturable: bool,
                             differentiable: bool):
    savs = []
    for i, param in enumerate(params):
        g = grads[i]
        v = exp_avgs[i]
        n = exp_avg_sqs[i]
        step_t = state_steps[i]
        ME = MEs[i]
        r_tilde = r_tildes[i]
        init_lr = init_lrs[i]
        lr = lrs[i]
        K = Ks[i]

        # If compiling, the compiler will handle cudagraph checks, see note [torch.compile x capturable]
        if capturable and not torch._utils.is_compiling():
            assert (
                (param.is_cuda and step_t.is_cuda) or (param.is_xla and step_t.is_xla)
            ), "If capturable=True, params and state_steps must be CUDA or XLA tensors."

        # update step
        step_t += 1

        if capturable:
            step = step_t
            ME_last = ME.clone()
        else:
            step = step_t.item()
            ME_last = ME.item()

        ME = float(coef['ME_v'](lr, beta1)) * torch.sum(v * v) + float(coef['ME_f'](lr, beta1)) * loss
        MEs[i].copy_(ME)

        if ME - r_tilde > r_tilde * K / ME_last:
            xi = 1 - (nu * r_tilde * K / ME_last / (ME - r_tilde)).item()
            xi = max(xi, 0)
        else:
            xi = 0
        r = xi * r_tilde + (1 - xi) * ME

        if adaptive:
            n = beta2 * n + (1 - beta2) * torch.sum(g * g)
            exp_avg_sqs[i].copy_(n)
            hat_n = n / (1 - beta2**(step))
            lr = init_lr / (torch.sqrt(hat_n) + eps) * (1 - beta1) / (1 - beta1**(step))
        lrs[i].copy_(lr)

        tmp = float(coef['tmp_v'](lr, beta1)) * v + float(coef['tmp_g'](lr, beta1)) * g
        K = float(coef['K_tmp'](lr, beta1))*torch.sum(tmp * tmp) + float(coef['K_g'](lr, beta1))*torch.sum(g * g)
        Ks[i].copy_(K)
        r_tilde = r / (1 + K / ME)
        r_tildes[i].copy_(r_tilde)

        m_indicator = (r / ME).item() if MSAV else 1
        v = m_indicator * float(coef['v_v'](lr, beta1)) * v + r_tilde / ME * float(coef['v_g'](lr, beta1)) * g
        exp_avgs[i].copy_(v)

        if opL == "trivial":
            update = float(coef['theta_v'](lr, beta1)) * v + r_tilde / ME * float(coef['theta_g'](lr, beta1)) * g
            param.add_(update)
        elif opL == "diag_hessian":
            # TODO: to be implemented
            pass
        else:
            raise ValueError("Invalid linear operator `opL`. Choose 'trivial' or 'diag_hessian'.")
        
        savs.append((r / ME).item())
    return savs




class NAdam_ERSAV(Optimizer):
    fr"""Combines the NAdam method with the
        Relaxed Scalar Auxiliary Variable (RSAV) algorithm.

    ..math::

    Args:
    ----------
        params (iterable): iterable of parameters to optimize or dicts defining parameter groups
        init_loss (Tensor): initial loss value
        lr (float): initial step-size
        lr_min (float, optional): not used, kept for compatibility
                                  lower bound of step-size (default: 0.01)
        opL (str, optional): linear operator for stabilization (default: 'trivial')
                             options: 'trivial': zero operator, 'diag_hessian': diagonal of Hessian matrix of f(x)
        nu (float, optional): relaxation constant which is less than 1 (default: 0.99)
        beta1 (float, optional): coefficients used for computing running averages of gradient (default: 0.9)
        beta2 (float, optional): coefficients used for computing running averages of squared gradient (default: 0.999)
        eps (float, optional): term added to the denominator to improve numerical stability (default: 1e-8)
        adaptive (bool, optional): whether to use adaptive step-size (default: True)
        MSAV (bool, optional): whether to multiply momentum with the SAV indicator (default: False)
        capturable (bool, optional): not implemented yet.
        differentiable (bool, optional): not implemented yet.
    """

    def __init__(self,
                 params, 
                 lr: float, 
                 lr_min: float = 0.01, 
                 opL: str = 'trivial', 
                 nu: float = 0.99, 
                 beta1: float = 0.9,
                 beta2: float = 0.999,
                 eps: float = 1e-8,
                 adaptive: bool = True,
                 MSAV: bool = False,
                 capturable: bool = False,
                 differentiable: bool = False,
                ):

        #################################################
        # build the symbolic expressions for update rules    
        self.coef = {}
        self.coef['ME_v'] = lambda eta, beta1: beta1**3 / 2 * eta
        self.coef['ME_f'] = lambda eta, beta1: 2 - beta1
        self.coef['tmp_v'] = lambda eta, beta1: eta * beta1
        self.coef['tmp_g'] = lambda eta, beta1: -eta
        self.coef['K_tmp'] = lambda eta, beta1: (1 - beta1) / eta
        self.coef['K_g'] = lambda eta, beta1: eta

        self.coef['v_v'] = lambda eta, beta1: beta1
        self.coef['v_g'] = lambda eta, beta1: -1
        self.coef['theta_v'] = lambda eta, beta1: eta * beta1
        self.coef['theta_g'] = lambda eta, beta1: -eta
        #################################################

        defaults = dict(lr=lr, lr_min=lr_min, opL=opL, savs_history=[],
                        nu=nu, beta1=beta1, beta2=beta2, eps=eps, adaptive=adaptive, MSAV=MSAV,
                        capturable=capturable, differentiable=differentiable)
        super(NAdam_ERSAV, self).__init__(params, defaults)


    def __setstate__(self, state):
        super().__setstate__(state)
        # code for checkpoint compatibility
        for group in self.param_groups:
            group.setdefault('capturable', False)
            group.setdefault('differentiable', False)
        state_values = list(self.state.values())
        step_is_tensor = (len(state_values) != 0) and torch.is_tensor(state_values[0]['step'])
        if not step_is_tensor:
            for s in state_values:
                s['step'] = torch.tensor(float(s['step']))

    def _init_group(self, group, params_with_grad, grads, exp_avgs, exp_avg_sqs, state_steps, 
                    loss, MEs, r_tildes, init_lrs, lrs, Ks):
        for p in group['params']:
            if p.grad is not None:
                params_with_grad.append(p)
                if p.grad.is_sparse:
                    raise RuntimeError('NAdam does not support sparse gradients')
                grads.append(p.grad)

                state = self.state[p]
                # Lazy state initialization
                if len(state) == 0:
                    # note(crcrpar): [special device hosting for step]
                    # Deliberately host `step` and `mu_product` on CPU if capturable is False.
                    # This is because kernel launches are costly on CUDA and XLA.
                    state['step'] = (
                        torch.zeros((), dtype=torch.float, device=p.device)
                        if group['capturable'] else torch.tensor(0.)
                    )
                    # Exponential moving average of gradient values
                    state['exp_avg'] = torch.zeros_like(p, memory_format=torch.preserve_format)
                    # Exponential moving average of squared gradient values
                    state['exp_avg_sq'] = torch.zeros_like(p, memory_format=torch.preserve_format)
                    # state['exp_avg_sq'] = torch.tensor(0, dtype=p.dtype, device=p.device)
                    # modified energy (ME) and scalar auxilary variable (r)
                    state['ME'] = self.coef['ME_f'](group['lr'], group['beta1']) * loss + torch.zeros_like(p, memory_format=torch.preserve_format)
                    state['r_tilde'] = state['ME'].clone()
                    # state['init_lr'] = torch.tensor(float(group['lr']))
                    # state['lr'] = torch.tensor(float(group['lr']))
                    state['init_lr'] = torch.tensor(group['lr'], dtype=p.dtype, device=p.device)
                    state['lr'] = group['lr'] * torch.ones_like(p, memory_format=torch.preserve_format) 
                    state['K'] = torch.zeros_like(p, memory_format=torch.preserve_format)

                exp_avgs.append(state['exp_avg'])
                exp_avg_sqs.append(state['exp_avg_sq'])
                state_steps.append(state['step'])
                MEs.append(state['ME'])
                r_tildes.append(state['r_tilde'])
                init_lrs.append(state['init_lr'])
                lrs.append(state['lr'])
                Ks.append(state['K'])

    @torch.no_grad()
    def step(self, closure):
        """Performs a single optimization step.

        Args:
            closure (Callable): A closure that reevaluates the model
                and returns the loss.
        """
        self._cuda_graph_capture_health_check()

        # Make sure the closure is always called with grad enabled
        closure = torch.enable_grad()(closure)
        loss = closure()

        for group in self.param_groups:
            params_with_grad = []
            grads = []
            exp_avgs = []
            exp_avg_sqs = []
            state_steps = []
            MEs = []
            r_tildes = []
            init_lrs = []
            lrs = []
            Ks = []

            self._init_group(group, params_with_grad, grads, exp_avgs, exp_avg_sqs, state_steps, 
                             loss, MEs, r_tildes, init_lrs, lrs, Ks)

            savs = _single_tensor_NAdam_ERSAV(params_with_grad,
                                    grads,
                                    exp_avgs,
                                    exp_avg_sqs,
                                    state_steps,
                                    loss=loss,
                                    MEs=MEs,
                                    r_tildes=r_tildes,
                                    Ks=Ks,
                                    init_lrs=init_lrs,
                                    lrs=lrs,
                                    lr_min=group['lr_min'],
                                    opL=group['opL'],
                                    nu=group['nu'],
                                    beta1=group['beta1'],
                                    beta2=group['beta2'],
                                    eps=group['eps'],
                                    adaptive=group['adaptive'],
                                    MSAV=group['MSAV'],
                                    coef=self.coef,
                                    capturable=group['capturable'],
                                    differentiable=group['differentiable'])
            # group['savs_history'].append(savs)
            # TODO: _multi_tensor version is not implemented yet
        return loss




def _single_tensor_NAdam_ERSAV(params: List[Tensor],
                             grads: List[Tensor],
                             exp_avgs: List[Tensor],
                             exp_avg_sqs: List[Tensor],
                             state_steps: List[Tensor],
                             loss: Optional[Tensor],
                             MEs: List[Tensor],
                             r_tildes: List[Tensor],
                             Ks: List[Tensor],
                             *,
                             init_lrs: List[float],
                             lrs: List[float],
                             lr_min: float,
                             opL: str,
                             nu: float,
                             beta1: float,
                             beta2: float,
                             eps: float,
                             adaptive: bool,
                             MSAV: bool,
                             coef: dict,
                             capturable: bool,
                             differentiable: bool):
    savs = []
    for i, param in enumerate(params):
        g = grads[i]
        v = exp_avgs[i]
        n = exp_avg_sqs[i]
        step_t = state_steps[i]
        ME = MEs[i]
        r_tilde = r_tildes[i]
        init_lr = init_lrs[i]
        lr = lrs[i]
        K = Ks[i]

        # If compiling, the compiler will handle cudagraph checks, see note [torch.compile x capturable]
        if capturable and not torch._utils.is_compiling():
            assert (
                (param.is_cuda and step_t.is_cuda) or (param.is_xla and step_t.is_xla)
            ), "If capturable=True, params and state_steps must be CUDA or XLA tensors."

        # update step
        step_t += 1

        if capturable:
            step = step_t
            ME_last = ME.clone()
        else:
            step = step_t.item()
            ME_last = ME.clone()

        ME = coef['ME_v'](lr, beta1) * (v * v.conj()) + coef['ME_f'](lr, beta1) * loss
        MEs[i].copy_(ME)

        mask = (ME - r_tilde) > (r_tilde * K / ME_last)
        xi = torch.zeros_like(ME)
        xi[mask] = 1 - nu * r_tilde[mask] * K[mask] / ME_last[mask] / (ME[mask] - r_tilde[mask])
        xi = torch.maximum(xi, torch.tensor(0.))
        r = xi * r_tilde + (1 - xi) * ME

        if adaptive:
            n = beta2 * n + (1 - beta2) * (g * g.conj())
            exp_avg_sqs[i].copy_(n)
            hat_n = n / (1 - beta2**(step))
            lr = init_lr / (torch.sqrt(hat_n) + eps) * (1 - beta1) / (1 - beta1**(step))
        lrs[i].copy_(lr)

        tmp = coef['tmp_v'](lr, beta1) * v + coef['tmp_g'](lr, beta1) * g
        K = coef['K_tmp'](lr, beta1)*(tmp * tmp.conj()) + coef['K_g'](lr, beta1)*(g * g.conj())
        Ks[i].copy_(K)
        r_tilde = r / (1 + K / ME)
        r_tildes[i].copy_(r_tilde)

        m_indicator = r / ME if MSAV else 1
        v = m_indicator * coef['v_v'](lr, beta1) * v + r_tilde / ME * coef['v_g'](lr, beta1) * g
        exp_avgs[i].copy_(v)

        if opL == "trivial":
            update = coef['theta_v'](lr, beta1) * v + r_tilde / ME * coef['theta_g'](lr, beta1) * g
            param.add_(update)
        elif opL == "diag_hessian":
            # TODO: to be implemented
            pass
        else:
            raise ValueError("Invalid linear operator `opL`. Choose 'trivial' or 'diag_hessian'.")
        
        # savs.append((r / ME).item())
    return savs