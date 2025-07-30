import sympy as sp
from ..base import ThreeParamGate, FourParamGate
from ..utils import sp_exp_i

class UGate(ThreeParamGate):
    def matrix(self):
        theta, phi, lam = self.theta, self.phi, self.lam
        return sp.Matrix([
            [sp.cos(theta / 2), -sp_exp_i(lam) * sp.sin(theta / 2)],
            [sp_exp_i(phi) * sp.sin(theta / 2), sp_exp_i(phi + lam) * sp.cos(theta / 2)]
        ])

class CUGate(FourParamGate):
    def matrix(self):
        theta, phi, lam = self.theta, self.phi, self.lam
        cos = sp.cos(theta / 2)
        sin = sp.sin(theta / 2)
        gph = sp_exp_i(self.gamma)
        return sp.Matrix([
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, gph * cos, - gph * sp_exp_i(lam) * sin],
            [0, 0, gph * sp_exp_i(phi) * sin, gph * sp_exp_i(phi + lam) * cos]
        ])
