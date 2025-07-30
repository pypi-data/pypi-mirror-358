import os
import sys
import json
import shutil
import numpy as np
from lxml import etree
from pymatgen.io.vasp.outputs import Vasprun


def extract_from_lammps(species: str,
                        lammps: str,
                        prefix_pos: str,
                        prefix_force: str,
                        prefix_cond: str):
    """
    Will be updated.
    """
    pass

def extract_from_vasp(species: str,
                      vasprun: str = "vasprun.xml",
                      prefix_pos: str = "pos",
                      prefix_force: str = "force",
                      prefix_cond: str = "cond"):
    """
    Extracting VacHopPy input files from vasprun.xml.
    Atomic trajectories are unwrapped according to PBC condition.

    Args:
        species (str): atom species (e.g., "O").
        vasprun (str, optional): vasprun.xml file. Defaults to "vasprun.xml".
        prefix_pos (str, optional): prefix for pos file. Defaults to "pos".
        prefix_force (str, optional): prefix for force file. Defaults to "force".
        prefix_cond (str, optional): prefix for cond file. Defaults to "cond".
    """

    if not os.path.isfile(vasprun):
        print(f"{vasprun} is not found.")
        sys.exit(0)

    v = Vasprun(vasprun, 
                parse_dos=False, 
                parse_eigen=False,
                parse_potcar_file=False)
    structure = v.final_structure
    atom_symbols = [str(site.specie) for site in structure.sites]

    # Atom count dictionary
    from collections import Counter
    atom_counts = dict(Counter(atom_symbols))

    # Target indices for selected species
    target_indices = [i for i, sym in enumerate(atom_symbols) if sym == species]
    if not target_indices:
        raise ValueError(f"No atoms with symbol '{species}' found.")

    iterations = v.ionic_steps
    nsw = len(iterations)
    n_atoms = len(target_indices)

    pos = np.zeros((nsw, n_atoms, 3), dtype=np.float64)
    force = np.zeros((nsw, n_atoms, 3), dtype=np.float64)

    for step_idx, step in enumerate(iterations):
        for j, atom_idx in enumerate(target_indices):
            pos[step_idx, j, :] = step["structure"].sites[atom_idx].frac_coords
            force[step_idx, j, :] = step["forces"][atom_idx]

    # PBC refinement
    displacement = np.zeros_like(pos)
    displacement[0:] = 0
    displacement[1:, :] = np.diff(pos, axis=0)
    displacement[displacement>0.5] -= 1.0
    displacement[displacement<-0.5] += 1.0
    displacement = np.cumsum(displacement, axis=0)
    pos = pos[0] + displacement
    
    # save positions and forces
    np.save(f"{prefix_pos}.npy", pos)
    np.save(f"{prefix_force}.npy", force)
    print(f"{prefix_pos}.npy is created.")
    print(f"{prefix_force}.npy is created.")

    # Extract metadata
    incar = v.incar
    potim = float(incar.get("POTIM", -1))
    nblock = int(incar.get("NBLOCK", -1))
    tebeg = float(incar.get("TEBEG", -1))
    teend = float(incar.get("TEEND", -1))

    if tebeg != teend:
        raise ValueError(f"TEBEG ({tebeg}) and TEEND ({teend}) are not equal.")

    lattice = structure.lattice.matrix.tolist()  # 3x3 list

    cond = {
        "symbol": species,
        "nsw": nsw,
        "potim": potim,
        "nblock": 1, # for vasprun.xml, all steps are stored
        "temperature": tebeg,
        "atom_counts": atom_counts,
        "lattice": lattice
    }
    
    cond_file = f"{prefix_cond}.json"
    with open(cond_file, "w") as f:
        json.dump(cond, f, indent=2)

    print(f"{cond_file} is created.")


def combine_vasprun(vasprun1, 
                    vasprun2,
                    vasprun_out = "vasprun_combined.xml"):
    # Load and merge files
    v1 = etree.parse(vasprun1)
    v2 = etree.parse(vasprun2)

    r1 = v1.getroot()
    r2 = v2.getroot()

    # remove duplicated <parameters> from v2
    p2 = r2.find("parameters")
    if p2 is not None:
        r2.remove(p2)

    # append calculations from v2
    calcs2 = r2.findall("calculation")
    for c in calcs2:
        r1.append(c)

    # recalculate total steps
    nsw_total = len(r1.findall("calculation"))

    # fix ALL <i name="NSW"> across entire tree
    for elem in r1.findall(".//i[@name='NSW']"):
        elem.text = str(nsw_total)

    # save result
    etree.ElementTree(r1).write(vasprun_out, pretty_print=True)
    

def crop_vasprun(vasprun,
                 nsw_crop,
                 vasprun_out="vasprun_cropped.xml"):
    print(f"Cropping first {nsw_crop} iterations from {vasprun}...")
    
    tree = etree.parse(vasprun)
    root = tree.getroot()

    calculations = root.findall(".//calculation")
    total = len(calculations)
    for calc in calculations[nsw_crop:]:
        calc.getparent().remove(calc)

    print(f"  Original steps: {total}, Cropped to: {nsw_crop}")

    # fix ALL <i name="NSW"> across entire tree
    for elem in root.findall(".//i[@name='NSW']"):
        elem.text = str(nsw_crop)

    tree.write(vasprun_out, pretty_print=True, encoding='utf-8', xml_declaration=True)
    print(f"Saved cropped file to {vasprun_out}")
 

def CosineDistance(fp1, fp2):
    """
    fp1 : fingerprint of structure 1
    fp2 : fingerprint of structure 2
    """
    dot = np.dot(fp1, fp2)
    norm1 = np.linalg.norm(fp1, ord=2)
    norm2 = np.linalg.norm(fp2, ord=2)

    return 0.5 * (1 - dot/(norm1*norm2))
