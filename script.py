from quality_assessor.quality_data_types import (TapeSpecs, TapeProduct)
from quality_assessor.quality_assessment import TapeQualityAssessor
from quality_assessor.tape_quality_information import TapeQualityInformation
from quality_assessor.quality_helper import load_data


def excecute_assessment(quality_info: TapeQualityInformation,
                        product: TapeSpecs) -> None:
    """ Do all the steps to assess a tape.

    Args:
        quality_info (TapeQualityInformation): Quality information about the tape
        product (TapeSpecs): Product definition to assess the tape against
    """
    assessor = TapeQualityAssessor(quality_info, product)

    assessor.assess_meets_specs()
    assessor.plot_dropout_histogram()
    assessor.determine_ok_tape_section(product.min_tape_length)

    assessor.save_pdf_report()
    assessor.print_reports()
    assessor.plot_defects()


def main():
    """ Main function of module to test functionality of classes in module
    """
    # from multiprocessing import Pool
    # from functools import partial

    product = TapeProduct.SUPERLINK_PHASE_TEST.value
    # expected_average = width * thickness * critical current density * factor
    # to fix units
    expected_average = product.width * 1.9 * 3 * 10
    expected_average = (product.min_average if product.min_average is not None
                        else expected_average)
    # quality_info = [
    #     TapeQualityInformation(
    #         load_data("data/20204-X-10_500A.dat", False), "20204-X-10",
    #         expected_average, product.average_length),
    #     TapeQualityInformation(
    #         load_data("data/17346-X-11-BL_30_29970_500A.dat", True),
    #         "17346-X-11", expected_average, product.average_length)
    # ]

    quality_info2 = [
        TapeQualityInformation(
            load_data("data/21407-3L-110_300A_Lam_Markiert.dat", False),
            "21407-3L-110", expected_average, product.average_length),
        TapeQualityInformation(
            load_data("data/21407-3M1-110_300A_Lam_Markiert.dat", False),
            "21407-3M1-110", expected_average, product.average_length),
        TapeQualityInformation(
            load_data("data/21407-3M2-110_300A_Lam_Markiert.dat", False),
            "21407-3M2-110", expected_average, product.average_length),
        TapeQualityInformation(
            load_data("data/21407-3R-110_300A_Lam_Mak.dat", False),
            "21407-R-110", expected_average, product.average_length),
        TapeQualityInformation(
            load_data("data/21413_3L-100_300A_Lam_Makiert.dat", False),
            "21413-L-100", expected_average, product.average_length),
        TapeQualityInformation(
            load_data("data/21413-3M1-100_300A_Lam_Makiert.dat", False),
            "21413-M1-100", expected_average, product.average_length),
        TapeQualityInformation(
            load_data("data/21413-3M2-100_300A_Lam_Markiert.dat", False),
            "21413-M2-100", expected_average, product.average_length),
        TapeQualityInformation(
            load_data("data/21413-3R-100_300A_Lam_Markiert.dat", False),
            "21413-R-100", expected_average, product.average_length),
    ]

    for info in quality_info2:
        excecute_assessment(info, product)

    # TODO Pool does not work with lambda expressions as callable
    # with Pool() as pool:
    #     pool.map(partial(excecute_assessment, product=product), quality_info)


if __name__ == '__main__':
    main()
