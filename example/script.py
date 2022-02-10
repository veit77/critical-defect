"""Example script to assess quality parameters of HTS tapes
"""
import os
from quality_assessment.data_types import TapeSpecs
from quality_assessment.products import TapeProduct
from quality_assessment.quality_assessor import TapeQualityAssessor
from quality_assessment.tape_quality_information import TapeQualityInformation
from quality_assessment.helper import load_data


def excecute_assessment(quality_info: TapeQualityInformation,
                        product: TapeSpecs) -> None:
    """ Do all the steps to assess a tape.

    Args:
        quality_info (TapeQualityInformation): Quality information about the tape
        product (TapeSpecs): Product definition to assess the tape against
    """
    assessor = TapeQualityAssessor(quality_info, product)

    assessor.assess_meets_specs()
    assessor.determine_ok_tape_section(product.min_tape_length)

    try:
        assessor.save_pdf_report("./reports")
    except ValueError as err:
        print(f"Can't save to given directory ({err}).")

    assessor.print_reports()
    # assessor.plot_dropout_histogram()
    # assessor.plot_defects()


def main():
    """ Main function of module to test functionality of classes in module
    """
    # from multiprocessing import Pool
    # from functools import partial

    product = TapeProduct.SUPERLINK_PHASE.value
    # expected_average = width * thickness * critical current density * factor
    # to fix units
    expected_average = product.width * 1.9 * 3 * 10
    expected_average = (product.min_average if product.min_average is not None
                        else expected_average)

    directory = "./data"
    file_list = os.listdir(directory)

    quality_info = []
    for file_name in file_list:
        name, extension = os.path.splitext(file_name)
        path = f'{directory}/{file_name}'
        if os.path.isfile(path) and extension == ".dat":
            q_info = TapeQualityInformation(load_data(path, None), name,
                                            expected_average)
            quality_info.append(q_info)

    # quality_info2 = [
    #     TapeQualityInformation(
    #         load_data("data/21407-3L-110_300A_Lam_Markiert.dat", False),
    #         "21407-3L-110", expected_average),
    #     TapeQualityInformation(
    #         load_data("data/21407-3M1-110_300A_Lam_Markiert.dat", False),
    #         "21407-3M1-110", expected_average),
    #     TapeQualityInformation(
    #         load_data("data/21407-3M2-110_300A_Lam_Markiert.dat", False),
    #         "21407-3M2-110", expected_average),
    #     TapeQualityInformation(
    #         load_data("data/21407-3R-110_300A_Lam_Mak.dat", False),
    #         "21407-R-110", expected_average),
    #     TapeQualityInformation(
    #         load_data("data/21413_3L-100_300A_Lam_Makiert.dat", False),
    #         "21413-L-100", expected_average),
    #     TapeQualityInformation(
    #         load_data("data/21413-3M1-100_300A_Lam_Makiert.dat", False),
    #         "21413-M1-100", expected_average),
    #     TapeQualityInformation(
    #         load_data("data/21413-3M2-100_300A_Lam_Markiert.dat", False),
    #         "21413-M2-100", expected_average),
    #     TapeQualityInformation(
    #         load_data("data/21413-3R-100_300A_Lam_Markiert.dat", False),
    #         "21413-R-100", expected_average),
    #     TapeQualityInformation(
    #         load_data("data/22005-3L-010_21705-3L-110_300A_Cu.dat", False),
    #         "22005-3L-010_21705-3L-110", expected_average),
    # ]

    for info in quality_info:
        excecute_assessment(info, product)

    # TODO Pool does not work with lambda expressions as callable
    # with Pool() as pool:
    #     pool.map(partial(excecute_assessment, product=product), quality_info)


if __name__ == '__main__':
    main()
