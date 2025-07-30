import argparse
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from .handlers import SHIK, BUCK, BUCK_EXT, TRUNC3B
from . import constants


def parse_args():
    parser = argparse.ArgumentParser(prog = "tablegen")

    subparsers = parser.add_subparsers(dest="command", required=True, metavar = "")
    shik = subparsers.add_parser("shik", help = "Argument parser for generating tables based on SHIK potentials.")

    shik.add_argument("structure_file", type = str, help = "Initial Structure File.")
    shik.add_argument("species", nargs = "+", type = str, default = constants.SHIK_SPECIES, help = "Map of species types (specified as space separated strings).")
    shik.add_argument("-c", "--cutoff", type = float, default = constants.CUTOFF, help = f"Table cutoff beyond which no potentials or forces will be generated. Default: {constants.CUTOFF} Å", metavar = '')
    shik.add_argument("-w", "--wolf_cutoff", type = float, default = constants.WOLF_CUTOFF, help = f"Wolf cutoff used for generation of the potential functions. Default: {constants.WOLF_CUTOFF} Å", metavar = '')
    shik.add_argument("-b", "--buck_cutoff", type = float, default = constants.BUCK_CUTOFF, help = f"Buckingham cutoff that specifies past which distance only wolf interactions are considered. Default: {constants.BUCK_CUTOFF} Å", metavar = '')
    shik.add_argument("-g", "--gamma", type = float, default = constants.GAMMA, help = f"Smoothing function width. Default: {constants.GAMMA} Å", metavar = '')
    shik.add_argument("-d", "--data_points", type = int, default = constants.DATAPOINTS, help = f"Number of points used in the table definition of the potential function. Default: {constants.DATAPOINTS}", metavar = '')
    shik.add_argument("-t", "--table_name", type = str, default = "SHIK.table", help = f"Name of the created table file. Default: SHIK.table", metavar = '')
    shik.add_argument("-p", "--plot", action = "store_true", default = False, help = f"Plotting switch. When included the potential functions will be plotted in matplotlib.")

    shik.set_defaults(handler_class = SHIK)


    buck = subparsers.add_parser("buck", help = "Argument parser for generating tables based on Buckingham potentials.")

    buck.add_argument("pairs", nargs = "+", type = str, default = [], help = "Pairs of atoms for potential energy and force curve generation. Example: Na-O Si-Na Si-O O-O.")
    buck.add_argument("-t", "--table_name", type = str, default = "BUCK.table", help = f"Name of the created table file. Default: BUCK.table", metavar = '')
    buck.add_argument("-c", "--cutoff", type = float, default = constants.CUTOFF, help = f"Table cutoff beyond which no potentials or forces will be generated. Default: {constants.CUTOFF} Å", metavar = '')
    buck.add_argument("-p", "--plot", nargs=2, type = float, default = None, help = f"Plotting switch. When included the potential functions will be plotted in matplotlib with lower and upper bound specified. Example: -p -10 10.", metavar = "")
    buck.add_argument("-d", "--data_points", type = int, default = constants.DATAPOINTS, help = f"Number of points used in the table definition of the potential function. Default: {constants.DATAPOINTS}", metavar = '')

    buck.set_defaults(handler_class = BUCK)


    buck_ext = subparsers.add_parser("buck_ext", help = "Argument parser for generating tables based on extended Buckingham potentials.")

    buck_ext.add_argument("pairs", nargs = "+", type = str, default = [], help = "Pairs of atoms for potential energy and force curve generation. Example: Na-O Si-Na Si-O O-O.")
    buck_ext.add_argument("-t", "--table_name", type = str, default = "BUCK.table", help = f"Name of the created table file. Default: BUCK.table", metavar = '')
    buck_ext.add_argument("-c", "--cutoff", type = float, default = constants.CUTOFF, help = f"Table cutoff beyond which no potentials or forces will be generated. Default: {constants.CUTOFF} Å", metavar = '')
    buck_ext.add_argument("-p", "--plot", nargs=2, type = float, default = None, help = f"Plotting switch. When included the potential functions will be plotted in matplotlib with lower and upper bound specified. Example: -p -10 10.", metavar = "")
    buck_ext.add_argument("-d", "--data_points", type = int, default = constants.DATAPOINTS, help = f"Number of points used in the table definition of the potential function. Default: {constants.DATAPOINTS}", metavar = '')


    buck_ext.set_defaults(handler_class = BUCK_EXT)

    trunc3b = subparsers.add_parser("3b_trunc", help = "Argument parser for generating tables based on three-body truncated harmonic potentials.")

    trunc3b.add_argument("triplets", nargs = "+", type = str, default = [], help = "Ttiplets of atoms in the format B-A-C where A is the central atom.")
    trunc3b.add_argument("-t", "--table_name", type = str, default = "TRUNC", help = f"Name (no extension) of two files that will be created - three-body + tabulated files. Default: TRUNC.3b, TRUNC.table", metavar = '')
    trunc3b.add_argument("-d", "--data_points", type = int, default = constants.DATAPOINTS3B, help = f"Number of steps used in tabulating interatomic separation distances. Angle is tabulated with 2N entries. In symmetric case the number of table entries will be M = (N+1)N^2 and in asymmetric 2N^3. Default: {constants.DATAPOINTS3B}", metavar = '')
    trunc3b.add_argument("-c", "--cutoff", type = float, default = constants.CUTOFF3B, help = f"Table cutoff beyond which no potentials or forces will be generated. Default: {constants.CUTOFF3B} Å", metavar = '')

    trunc3b.set_defaults(handler_class = TRUNC3B)


    return parser.parse_args()

def two_body(handler):
    file = open(handler.table_name, "w")
    radius = np.linspace(0, float(handler.CUTOFF), handler.DATAPOINTS + 1)[1:]
    num_digits = len(str(handler.DATAPOINTS))

    visited = list()
    for spec1 in handler.SPECIES:
        for spec2 in handler.SPECIES:
            pair_name = handler.get_pair_name(spec1, spec2)
            if pair_name:
                if pair_name not in visited:
                    print(f"Pair name for {spec1} and {spec2} is {pair_name}")
                    visited.append(pair_name)
                    file.write(pair_name + "\n")
                    file.write(f"N {handler.DATAPOINTS}\n\n")
                    potential = []
                    force = []
                    for i, r in enumerate(radius):
                        force_val = handler.eval_force(spec1, spec2, r)
                        force.append(force_val)
                        pot_val = handler.eval_pot(spec1, spec2, r)
                        potential.append(pot_val)
                        file.write(str(i + 1).rjust(num_digits) + "  " + f"{r:.6E}".center(16) + f"{potential[i]:.6E}".center(16) + f"{force[i]:.6E}".rjust(14) + "\n")
                    file.write("\n\n")
                    if handler.plot:
                        plt.plot(radius, potential, label = pair_name)

            else:
                msg = handler.no_spec_msg(spec1, spec2)
                if msg:
                    print(msg)

    file.close()
    if handler.plot:
        plt.axhline(0, color='black', linewidth=1, linestyle = '--')
        plt.xlabel("Separation Distance (Å)")
        plt.ylabel("Potential Energy (eV)")
        plt.ylim(*handler.plot)
        plt.legend()
        plt.show()

def three_body(handler):
    
    tb_file = open(handler.TABLENAME + ".3b", "w")
    
    tb_text = str()
    for triplet in handler.TRIPLETS:
        tb_text += "\n".join(triplet) + "\n"
        tb_text += f"{handler.CUTOFF}\n"
        tb_text += handler.TABLENAME + ".table\n"
        tb_text += "-".join(triplet) + "\n"
        tb_text += "linear\n"
        tb_text += f"{handler.DATAPOINTS}\n"

    tb_file.write(tb_text)
    tb_file.close()

    tabulated_text = str()
    for triplet in handler.TRIPLETS:
        triplet_name = "-".join(triplet)
        tabulated_text += triplet_name + "\n"
        tabulated_text += f"N {handler.DATAPOINTS} rmin {handler.CUTOFF/handler.DATAPOINTS} rmax {handler.CUTOFF}\n\n"

        ctr = 0
        if triplet[0] == triplet[2]:
            print(f"Triplet {triplet_name} is symmetric. Working on generating a table of {(handler.DATAPOINTS**2) * (handler.DATAPOINTS + 1)} entries")
            for step, rij in enumerate(np.linspace(0, handler.CUTOFF, handler.DATAPOINTS + 1)[1:]):
                for rik in np.linspace(rij, handler.CUTOFF, handler.DATAPOINTS - step):
                    for theta in np.linspace(np.pi/(4*handler.DATAPOINTS), np.pi - np.pi/(4*handler.DATAPOINTS), 2*handler.DATAPOINTS):
                        ctr += 1
                        force_porj = " ".join(map(str, handler.get_force_coeffs(triplet_name, rij, rik, theta)))
                        tabulated_text += f"{ctr} {rij} {rik} {theta * 180 / np.pi} {force_porj} {handler.get_pot(triplet_name, rij, rik, theta)}\n"

                print(f"Generated entries for rij = {rij}")

        else:
            print(f"Triplet {triplet_name} is asymmetric. Working on generating a table of {2*(handler.DATAPOINTS**3)} entries")
            for step, rij in enumerate(np.linspace(0, handler.CUTOFF, handler.DATAPOINTS + 1)[1:]):
                for rik in np.linspace(0, handler.CUTOFF, handler.DATAPOINTS + 1)[1:]:
                    for theta in np.linspace(np.pi/(4*handler.DATAPOINTS), np.pi - np.pi/(4*handler.DATAPOINTS), 2*handler.DATAPOINTS):
                        ctr += 1
                        force_porj = " ".join(map(str, handler.get_force_coeffs(triplet_name, rij, rik, theta)))
                        tabulated_text += f"{ctr} {rij} {rik} {theta * 180 / np.pi} {force_porj} {handler.get_pot(triplet_name, rij, rik, theta)}\n"

                print(f"Generated entries for rij = {rij}")

    tab_file = open(handler.TABLENAME + ".table", "w")
    tab_file.write(tabulated_text)
    tab_file.close()




def main():
    args = parse_args()

    handler = args.handler_class(args)

    (two_body if handler.is_2b else three_body)(handler)


if __name__ == "__main__":
    main()
