import re, sys
import numpy as np
import mpmath as mp
from tablegen import constants

class TRUNC3B:
    
    def __init__(self, args):
        self.is_2b = False
        self.TABLENAME = args.table_name
        self.CUTOFF = float(args.cutoff)
        self.DATAPOINTS = args.data_points

        self.TRIPLETS = list()
        self.TRIPLET_NAMES = list()
        for triplet in args.triplets:
            nowhite = re.sub(r'\s+', '', triplet)
            self.TRIPLET_NAMES.append(nowhite)
            split_triplet = nowhite.split("-")
            if len(split_triplet) == 3:
                self.TRIPLETS.append(split_triplet)
            else:
                raise RuntimeError("Each triplet has to contain three elements (two dashes). Please read the help message for any three-body generator.")

        self.COEFFS = dict()
        for triplet in self.TRIPLET_NAMES:
            try:
                k = float(input(f"({triplet}) k: "))
            except ValueError:
                print("Truncated three-body potential coefficients should be real numbers.")
                sys.exit()
            try:
                rho = float(input(f"({triplet}) rho: "))
            except ValueError:
                print("Truncated three-body potential coefficients should be real numbers.")
                sys.exit()
            try:
                theta0 = float(input(f"({triplet}) theta-naught: ")) * mp.pi / 180
            except ValueError:
                print("Truncated three-body potential coefficients should be real numbers.")
                sys.exit()

            self.COEFFS[triplet] = [k, rho, theta0]

    def triplet_energy(self, rij, rik, theta, k, rho, theta0):
        rij      = mp.mpf(rij)
        rik      = mp.mpf(rik)
        theta    = mp.mpf(theta)
        theta0   = mp.mpf(theta0)
        k        = mp.mpf(k)
        rho      = mp.mpf(rho)
    
        A = mp.e ** (-(rij**8 + rik**8) / rho**8)
        return mp.mpf('0.5') * k * (theta - theta0) ** 2 * A

    def get_pot(self, triplet, rij, rik, theta):
        return float(self.triplet_energy(rij, rik, theta, *self.COEFFS[triplet]))

    def get_force_coeffs(self, triplet, rij, rik, theta):
        return self.projection_coeffs(rij, rik, theta, *self.COEFFS[triplet])


    def projection_coeffs(self, rij, rik, theta, k, rho, theta0):
        """
        Return the six scalar projection coefficients required by
        LAMMPS threebody/table (fi1, fi2, fj1, fj2, fk1, fk2)
        , all as floats.
    
        Internally everything is computed with mpmath.
        """
        # Promote scalars ----------------------------------------------------
        rij      = mp.mpf(rij)
        rik      = mp.mpf(rik)
        theta    = mp.mpf(theta)
        theta0   = mp.mpf(theta0)
        k        = mp.mpf(k)
        rho      = mp.mpf(rho)
    
        # 2-D embedding of the triangle ------------------------------------
        r_i = mp.matrix([rij, 0, 0])
        r_j = mp.matrix([0,   0, 0])
        r_k = mp.matrix([rik * mp.cos(theta),
                         rik * mp.sin(theta), 0])
    
        d_ij, d_ik = r_i - r_j, r_i - r_k
        d_ji, d_jk = -d_ij,     r_j - r_k
        d_ki, d_kj = -d_ik,    -d_jk
    
        e_ij = d_ij / mp.norm(d_ij)
        e_ik = d_ik / mp.norm(d_ik)
        c    = (e_ij.T * e_ik)[0]
        s    = mp.sqrt(1 - c ** 2) if c**2 < 1 else mp.mpf('0')
    
        # Energy & derivatives ---------------------------------------------
        U        = self.triplet_energy(rij, rik, theta, k, rho, theta0)
        U_theta  = k * (theta - theta0) * mp.e ** (-(rij**8 + rik**8) / rho**8)
        U_rij    = -8 * rij**7 / rho**8 * U
        U_rik    = -8 * rik**7 / rho**8 * U
        g_i      = U_theta / (rij * s) if s != 0 else mp.mpf('0')
        g_k      = U_theta / (rik * s) if s != 0 else mp.mpf('0')
    
        # Forces ------------------------------------------------------------
        F_i = ((8 * rij**7 / rho**8) * U * e_ij +
               (8 * rik**7 / rho**8) * U * e_ik +
               g_i * (c * e_ij - e_ik) +
               g_k * (c * e_ik - e_ij))
    
        F_j = ((8 * rij**7 / rho**8) * U * e_ij +
               g_i * (e_ik - c * e_ij))
    
        F_k = ((8 * rik**7 / rho**8) * U * e_ik +
               g_k * (e_ij - c * e_ik))

    
        # Utility to solve projection --------------------------------------
        def proj_coeffs(F, v1, v2):
            M = mp.matrix([[ (v1.T * v1)[0], (v1.T * v2)[0] ],
                           [ (v2.T * v1)[0], (v2.T * v2)[0] ]])
            rhs = mp.matrix([[ (F.T * v1)[0] ],
                             [ (F.T * v2)[0] ]])
            a, b = mp.lu_solve(M, rhs)
            return a, b
    
        fi1, fi2 = proj_coeffs(F_i, d_ij, d_ik)
        fj1, fj2 = proj_coeffs(F_j, d_ji, d_jk)
        fk1, fk2 = proj_coeffs(F_k, d_ki, d_kj)
    
        # Cast to plain floats right before returning -----------------------
        return float(fi1), float(fi2), float(fj1), float(fj2), float(fk1), float(fk2)
