# Copyright 2025 ByteDance and/or its affiliates.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from pathlib import Path

import click

from pxmeter.configs.data_config import COMPONENTS_FILE, download_ccd_cif
from pxmeter.eval import evaluate, MetricResult
from pxmeter.utils import none_or_str, read_chain_id_to_mol_from_json


def run_eval_cif(
    ref_cif: Path,
    model_cif: Path,
    output_json: Path,
    ref_model: int = 1,
    ref_assembly_id: str | None = None,
    ref_altloc: str = "first",
    interested_lig_label_asym_id: str | None = None,
    chain_id_to_mol_json: str | None = None,
    output_mapped_cif: bool = False,
) -> MetricResult:
    """
    Evaluate the performance of a model CIF file against a reference CIF file.
    And save the result to a JSON file.
    """
    if chain_id_to_mol_json:
        chain_id_to_mol = read_chain_id_to_mol_from_json(chain_id_to_mol_json)
    else:
        chain_id_to_mol = None

    if interested_lig_label_asym_id is not None:
        # split by comma
        interested_lig_label_asym_id = interested_lig_label_asym_id.split(",")

    metric_result = evaluate(
        ref_cif=ref_cif,
        model_cif=model_cif,
        ref_model=ref_model,
        ref_assembly_id=ref_assembly_id,
        ref_altloc=ref_altloc,
        interested_lig_label_asym_id=interested_lig_label_asym_id,
        model_chain_id_to_lig_mol=chain_id_to_mol,
    )

    metric_result.to_json(json_file=output_json)

    if output_mapped_cif:
        ref_mapped_cif = str(output_json).replace(".json", "_mapped_ref.cif")
        model_mapped_cif = str(output_json).replace(".json", "_mapped_model.cif")

        # Select valid atoms of model also by in ref structure
        metric_result.ref_struct.to_cif(ref_mapped_cif)
        metric_result.model_struct.to_cif(model_mapped_cif)

    return metric_result


@click.group()
def ccd_cli():
    """
    CCD Options.
    """
    return


@ccd_cli.command(name="update")
def update():
    """
    Update the CCD database.
    """
    download_ccd_cif(output_path=COMPONENTS_FILE.parent)


@click.group()
def eval_cif():
    """
    Evaluate the performance of a model CIF file against a reference CIF file.
    """
    return


@click.group(invoke_without_command=True)
@click.option(
    "-r", "--ref_cif", type=Path, required=True, help="Path to the reference CIF file."
)
@click.option(
    "-m", "--model_cif", type=Path, required=True, help="Path to the model CIF file."
)
@click.option(
    "-o",
    "--output_json",
    type=Path,
    default="./pxm_output.json",
    help="Path to the output JSON file. Defaults to 'pxm_output.json'.",
)
@click.option(
    "--ref_model",
    type=int,
    default=1,
    help="Model number in the reference CIF file to use. Defaults to 1.",
)
@click.option(
    "--ref_assembly_id",
    type=none_or_str,
    default=None,
    help="Assembly ID in the reference CIF file. Defaults to None.",
)
@click.option(
    "--ref_altloc",
    type=str,
    default="first",
    help="Altloc ID in the reference CIF file. Defaults to 'first'.",
)
@click.option(
    "-l",
    "--interested_lig_label_asym_id",
    type=none_or_str,
    default=None,
    help="The label_asym_id of the ligand of interest in the reference structure (for ligand RMSD metrics). \
            If multiple ligands are present, separate them by comma. Defaults to None.",
)
@click.option(
    "-c",
    "--chain_id_to_mol_json",
    type=none_or_str,
    default=None,
    help="Path to a JSON file containing a mapping of chain IDs to molecular input (SMILES). \
        E.g. {'B': 'c1ccccc1', 'D':'CCCC'}",
)
@click.option(
    "--output_mapped_cif",
    is_flag=True,
    help="Whether to output the mapped CIF file. Defaults to False.",
)
def run_eval_cif_cli(
    ref_cif: Path,
    model_cif: Path,
    output_json: Path,
    ref_model: int = 1,
    ref_assembly_id: str | None = None,
    ref_altloc: str = "first",
    interested_lig_label_asym_id: str | None = None,
    chain_id_to_mol_json: str | None = None,
    output_mapped_cif: bool = False,
):
    """
    Evaluate the performance of a model CIF file against a reference CIF file.
    And save the result to a JSON file.
    """
    run_eval_cif(
        ref_cif,
        model_cif,
        output_json,
        ref_model,
        ref_assembly_id,
        ref_altloc,
        interested_lig_label_asym_id,
        chain_id_to_mol_json,
        output_mapped_cif,
    )
