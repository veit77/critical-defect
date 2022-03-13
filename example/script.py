"""Example script to assess quality parameters of HTS tapes
"""
import os
from enum import Enum
from math import exp
from quality_assessment.data_types import TapeSpecs
from quality_assessment.quality_assessor import TapeQualityAssessor
from quality_assessment.tape_quality_information import TapeQualityInformation
from quality_assessment.helper import load_data


def defect_width(from_ic: float, param_a=1.43587, param_b=0.027726) -> float:
    """Calculates the maximum allowed width of a defect given a I_c.

    Args:
        from_ic (float): Minimum I_c of the defect
        param_a (float, optional): Parameter a of the dependency. Defaults to 1.43587.
        param_b (float, optional): Parameter b of the dependency. Defaults to 0.027726.

    Returns:
        float: maximum width the defect can have with the given I_c
    """
    return param_a * exp(param_b * from_ic)


class CustomTapeProduct(Enum):
    """ Enum summarizing different custom tape specifications
    """
    SUPERLINK_PHASE = TapeSpecs(
        width=3.0,
        min_tape_length=190.0,
        min_value=100.0,
        dropout_value=20.0,
        dropout_func=defect_width,
        width_from_true_baseline=False,
        min_average=135.0,
        averaging_length=1.0,
        description="Custom SuperLink Phase")
    SUPERLINK_NEUTRAL = TapeSpecs(
        width=6.0,
        min_tape_length=190.0,
        min_value=100.0,
        dropout_value=20.0,
        dropout_func=defect_width,
        min_average=180.0,
        width_from_true_baseline=False,
        averaging_length=1.0,
        description="Custom SuperLink Neutral")


def excecute_assessment(quality_info: TapeQualityInformation,
                        product: TapeSpecs, save_pdf_to: str,
                        **kwargs) -> None:
    """ Do all the steps to assess a tape.

    Args:
        quality_info (TapeQualityInformation): Quality information about the tape
        product (TapeSpecs): Product definition to assess the tape against
        save_pdf_to (str): directory to save the pdf reports to.
    """
    assessor = TapeQualityAssessor(quality_info, product)

    assessor.assess_meets_specs()
    assessor.determine_ok_tape_section(product.min_tape_length)

    try:
        assessor.save_pdf_report(save_pdf_to)
    except ValueError as err:
        print(f"Can't save to given directory ({err}).")

    for key in ('print_reports', 'plot_dropout_histogram', 'plot_defects'):
        if key in kwargs:
            if kwargs[key]:
                # Call function named 'key' from object 'assessor'
                method_call = getattr(assessor, key)
                method_call()

    # assessor.print_reports()
    # assessor.plot_dropout_histogram()
    # assessor.plot_defects()


def tape_data(from_dir: str,
              expected_average: float) -> list[TapeQualityInformation]:
    """ Generates a list of tape data from .dat files in a directory

    Args:
        from_dir (str): directory to load the data files from.
        expected_average (float): expected Ic level.

    Returns:
        list[TapeQualityInformation]: List of tape data objects.
    """
    file_list = os.listdir(from_dir)

    quality_info = []
    for file_name in file_list:
        name, extension = os.path.splitext(file_name)
        path = f'{from_dir}/{file_name}'
        if os.path.isfile(path) and extension == ".dat":
            q_info = TapeQualityInformation(load_data(path, None), name,
                                            expected_average)
            quality_info.append(q_info)
    return quality_info


def tape_data_from_list(expected_average: float) -> list[TapeQualityInformation]:
    """ return a manually compiled list of tape data

    Args:
        expected_average (float): expected Ic level.

    Returns:
        list[TapeQualityInformation]: List of tape data objects.
    """
    return [
        TapeQualityInformation(
            load_data("data/21407-3L-110_300A_Lam_Markiert.dat", False),
            "21407-3L-110", expected_average),
        TapeQualityInformation(
            load_data("data/21407-3M1-110_300A_Lam_Markiert.dat", False),
            "21407-3M1-110", expected_average),
        TapeQualityInformation(
            load_data("data/21407-3M2-110_300A_Lam_Markiert.dat", False),
            "21407-3M2-110", expected_average),
        TapeQualityInformation(
            load_data("data/21407-3R-110_300A_Lam_Mak.dat", False),
            "21407-R-110", expected_average),
        TapeQualityInformation(
            load_data("data/21413_3L-100_300A_Lam_Makiert.dat", False),
            "21413-L-100", expected_average),
        TapeQualityInformation(
            load_data("data/21413-3M1-100_300A_Lam_Makiert.dat", False),
            "21413-M1-100", expected_average),
        TapeQualityInformation(
            load_data("data/21413-3M2-100_300A_Lam_Markiert.dat", False),
            "21413-M2-100", expected_average),
        TapeQualityInformation(
            load_data("data/21413-3R-100_300A_Lam_Markiert.dat", False),
            "21413-R-100", expected_average),
        TapeQualityInformation(
            load_data("data/22005-3L-010_21705-3L-110_300A_Cu.dat", False),
            "22005-3L-010_21705-3L-110", expected_average),
    ]


def main():
    """ Main function of module to test functionality of classes in module
    """

    product = CustomTapeProduct.SUPERLINK_PHASE.value
    # expected_average = width * thickness * critical current density * factor
    # to fix units
    expected_average = product.width * 1.9 * 3 * 10
    expected_average = (product.min_average if product.min_average is not None
                        else expected_average)

    data_from_dir = "./data"
    quality_info = tape_data(from_dir=data_from_dir,
                             expected_average=expected_average)

    # quality_info = tape_data_from_list(expected_average)

    save_pdf_to_dir = "./reports"
    print_reports = True
    plot_defects = False
    plot_histograms = False

    if excecute_parallel := True:
        # Pool does not work with lambda expressions as callable
        from multiprocessing import Pool
        from functools import partial
        with Pool() as pool:
            pool.map(
                partial(excecute_assessment,
                        product=product,
                        save_pdf_to=save_pdf_to_dir,
                        print_reports=print_reports,
                        plot_defects=plot_defects,
                        plot_dropout_histogram=plot_histograms), quality_info)
    else:
        for info in quality_info:
            excecute_assessment(info,
                                product,
                                save_pdf_to_dir,
                                print_reports=print_reports,
                                plot_defects=plot_defects,
                                plot_dropout_histogram=plot_histograms)


if __name__ == '__main__':
    main()
