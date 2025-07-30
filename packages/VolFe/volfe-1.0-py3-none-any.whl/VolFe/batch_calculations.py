# batch_calculations.py

import pandas as pd
import datetime
import math as math
import warnings
import tqdm

import VolFe.melt_gas as mg
import VolFe.equilibrium_equations as eq
import VolFe.isotopes as iso
import VolFe.model_dependent_variables as mdv
import VolFe.calculations as c

################
# Contents #####
################
# building results tables
# options from setup file
# calculate the pressure of vapor saturation
# calculate de/regassing paths
# calculate isobars
# calculate solubility constants
# calculate fugacity coefficients
# Use melt S oxybarometer
# measured parameters within error
# Below this: in development

###############################
# building results tables #####
###############################


# outputing sample name
def results_table_sample_name(setup, run):
    """
    Creates DataFrames with headers and values for Sample name

    Parameters
    ----------
    setup: pandas.DataFrame
        DataFrame with melt compositions to be used.

    run: int
        Row number to be read from DataFrame

    Returns
    -------
    tuple(pandas.DataFrame,pandas.DataFrame)
        Header and value for sample name

    """
    results_headers = pd.DataFrame([["sample"]])
    results_values = pd.DataFrame([[setup.loc[run, "Sample"]]])
    return results_headers, results_values


# outputting melt composition, T, P
def results_table_melt_comp_etc(PT, melt_comp, conc, frac, melt_wf):
    """
    Creates DataFrames with headers and values for pressure, temperature, and melt
    composition (concentration and ratios)

    Parameters
    ----------
    PT: dict
        Pressure (bars) as "P" and temperature ('C) as "T"

    melt_comp: dict
        Melt composition in weight fraction (major and minor elements)

    conc: dict
        Volatile concentrations in the melt in weight fraction

    frac: dict
        Ratios of each species over volatile element

    melt_wf: dict
        Melt composition (specifically for sulfide composition)


    Returns
    -------
    tuple(pandas.DataFrame,pandas.DataFrame)
        Headers and values for pressure, temperature, and melt composition
        (concentration and ratios)

    """
    results_headers = pd.DataFrame(
        [
            [
                "T_C",
                "P_bar",
                "SiO2_wtpc",
                "TiO2_wtpc",
                "Al2O3_wtpc",
                "FeOT_wtpc",
                "MnO_wtpc",
                "MgO_wtpc",
                "CaO_wtpc",
                "Na2O_wtpc",
                "K2O_wtpc",
                "P2O5_wtpc",
                "H2OT_wtpc",
                "OH_wtpc",
                "H2Omol_wtpc",
                "H2_ppmw",
                "CH4_ppmw",
                "CO2T_ppmw",
                "CO2mol_ppmw",
                "CO2carb_ppmw",
                "CO_ppmw",
                "S2-_ppmw",
                "S6+_ppmw",
                "H2S_ppmw",
                "H_H2OT/HT",
                "H_H2/HT",
                "H_CH4/HT",
                "H_H2S/HT",
                "C_CO2T/CT",
                "C_CO/CT",
                "C_CH4/CT",
                "S2-/ST",
                "S6+/ST",
                "H2S/ST",
                "Fe3+/FeT",
                "sulf_XFe",
                "sulf_XCu",
                "sulf_XNi",
            ]
        ]
    )
    if "sulf_XFe" in melt_wf:
        melt_wf
    else:
        melt_wf["sulf_XFe"] = 1.0
    if "sulf_XCu" in melt_wf:
        melt_wf
    else:
        melt_wf["sulf_XCu"] = 0.0
    if "sulf_XNi" in melt_wf:
        melt_wf
    else:
        melt_wf["sulf_XNi"] = 0.0
    results_values = pd.DataFrame(
        [
            [
                PT["T"],
                PT["P"],
                melt_comp["SiO2"] * 100.0,
                melt_comp["TiO2"] * 100.0,
                melt_comp["Al2O3"] * 100.0,
                melt_comp["FeOT"] * 100.0,
                melt_comp["MnO"] * 100.0,
                melt_comp["MgO"] * 100.0,
                melt_comp["CaO"] * 100.0,
                melt_comp["Na2O"] * 100.0,
                melt_comp["K2O"] * 100.0,
                melt_comp["P2O5"] * 100.0,
                conc["wm_H2O"] * 100.0,
                conc["wm_OH"] * 100,
                conc["wm_H2Omol"] * 100.0,
                conc["wm_H2"] * 1000000.0,
                conc["wm_CH4"] * 1000000.0,
                conc["wm_CO2"] * 1000000.0,
                conc["wm_CO2mol"] * 1000000,
                conc["wm_CO2carb"] * 1000000,
                conc["wm_CO"] * 1000000.0,
                conc["wm_S2m"] * 1000000.0,
                conc["wm_S6p"] * 1000000.0,
                conc["wm_H2S"] * 1000000.0,
                frac["H2O_HT"],
                frac["H2_HT"],
                frac["CH4_HT"],
                frac["H2S_HT"],
                frac["CO2_CT"],
                frac["CO_CT"],
                frac["CH4_CT"],
                frac["S2m_ST"],
                frac["S6p_ST"],
                frac["H2S_ST"],
                melt_wf["Fe3FeT"],
                melt_wf["sulf_XFe"],
                melt_wf["sulf_XCu"],
                melt_wf["sulf_XNi"],
            ]
        ]
    )
    return results_headers, results_values


def results_table_melt_vol():
    """
    Creates DataFrame with headers for volatile concentrations in melt

    Returns
    -------
    pandas.DataFrame
        Headers for volatile concentrations in melt

    """
    results_headers = pd.DataFrame(
        [["H2OT-eq_wtpc", "CO2T-eq_ppmw", "ST_ppmw", "X_ppmw"]]
    )
    return results_headers


# outputting model options used in the calculation
def results_table_model_options(models):
    """
    Creates DataFrames with headers and values for options used in calculations and
    datetime of calculations

    Parameters
    ----------
    models: pandas.DataFrame
        Model options used in calculations

    Returns
    -------
    tuple(pandas.DataFrame,pandas.DataFrame)
        Headers and values for model options used in calculations and datetime of
        calculation
    """
    results_headers = pd.DataFrame(
        [
            [
                "setup opt",
                "COH_species opt",
                "H2S_m opt",
                "species X opt",
                "Hspeciation opt",
                "fO2 opt",
                "NNObuffer opt",
                "FMQbuffer opt",
                "carbon dioxide opt",
                "water opt",
                "hydrogen opt",
                "sulfide opt",
                "sulfate opt",
                "hydrogen sulfide opt",
                "methane opt",
                "carbon monoxide opt",
                "species X solubility opt",
                "Cspeccomp opt",
                "Hspeccomp opt",
                "SCSS opt",
                "SCAS opt",
                "sulfur_saturation opt",
                "sulfur_is_sat opt",
                "graphite_saturation opt",
                "ideal_gas opt",
                "y_CO2 opt",
                "y_SO2 opt",
                "y_H2S opt",
                "y_H2 opt",
                "y_O2 opt",
                "y_S2 opt",
                "y_CO opt",
                "y_CH4 opt",
                "y_H2O opt",
                "y_OCS opt",
                "y_X opt",
                "KHOg opt",
                "KHOSg opt",
                "KOSg opt",
                "KOSg2 opt",
                "KCOg opt",
                "KCOHg opt",
                "KOCSg opt",
                "KCOs opt",
                "carbonylsulfide opt",
                "density opt",
                "Date",
            ]
        ]
    )
    results_values = pd.DataFrame(
        [
            [
                models.loc["setup", "option"],
                models.loc["COH_species", "option"],
                models.loc["H2S_m", "option"],
                models.loc["species X", "option"],
                models.loc["Hspeciation", "option"],
                models.loc["fO2", "option"],
                models.loc["NNObuffer", "option"],
                models.loc["FMQbuffer", "option"],
                models.loc["carbon dioxide", "option"],
                models.loc["water", "option"],
                models.loc["hydrogen", "option"],
                models.loc["sulfide", "option"],
                models.loc["sulfate", "option"],
                models.loc["hydrogen sulfide", "option"],
                models.loc["methane", "option"],
                models.loc["carbon monoxide", "option"],
                models.loc["species X solubility", "option"],
                models.loc["Cspeccomp", "option"],
                models.loc["Hspeccomp", "option"],
                models.loc["SCSS", "option"],
                models.loc["SCAS", "option"],
                models.loc["sulfur_saturation", "option"],
                models.loc["sulfur_is_sat", "option"],
                models.loc["graphite_saturation", "option"],
                models.loc["ideal_gas", "option"],
                models.loc["y_CO2", "option"],
                models.loc["y_SO2", "option"],
                models.loc["y_H2S", "option"],
                models.loc["y_H2", "option"],
                models.loc["y_O2", "option"],
                models.loc["y_S2", "option"],
                models.loc["y_CO", "option"],
                models.loc["y_CH4", "option"],
                models.loc["y_H2O", "option"],
                models.loc["y_OCS", "option"],
                models.loc["y_X", "option"],
                models.loc["KHOg", "option"],
                models.loc["KHOSg", "option"],
                models.loc["KOSg", "option"],
                models.loc["KOSg2", "option"],
                models.loc["KCOg", "option"],
                models.loc["KCOHg", "option"],
                models.loc["KOCSg", "option"],
                models.loc["KCOs", "option"],
                models.loc["carbonylsulfide", "option"],
                models.loc["density", "option"],
                datetime.datetime.now(),
            ]
        ]
    )
    return results_headers, results_values


# outputting fugacities, partial pressures, gas mole fraction, fugacity coefficients,
# molecular masses, solubility constants, equilibrium constants, melt density
def results_table_f_p_xg_y_M_C_K_d(PT, melt_wf, models):
    """
    Creates DataFrames with headers and values for fO2, fugacities, partial pressures,
    vapor mole fractions, fugacity coefficients, molecular masses, solubility constants,
    equilibrium constants, and melt density

    Parameters
    ----------
    PT: dict
        Pressure (bars) as "P" and temperature ('C) as "T"

    melt_wf: dict:
        Melt composition

    models: pandas.DataFrame
        Model options used in calculations

    Returns
    -------
    tuple(pandas.DataFrame,pandas.DataFrame)
        Headers and values for for fO2, fugacities, partial pressures, vapor mole
        fractions, fugacity coefficients, molecular masses, solubility constants,
        equilibrium constants, and melt density
    """
    results_headers = pd.DataFrame(
        [
            [
                "fO2_DNNO",
                "fO2_DFMQ",
                "fO2_bar",
                "fH2_bar",
                "fH2O_bar",
                "fS2_bar",
                "fSO2_bar",
                "fH2S_bar",
                "fCO2_bar",
                "fCO_bar",
                "fCH4_bar",
                "fOCS_bar",
                "fX_bar",
                "pO2_bar",
                "pH2_bar",
                "pH2O_bar",
                "pS2_bar",
                "pSO2_bar",
                "pH2S_bar",
                "pCO2_bar",
                "pCO_bar",
                "pCH4_bar",
                "pOCS_bar",
                "pX_bar",
                "xgO2_mf",
                "xgH2_mf",
                "xgH2O_mf",
                "xgS2_mf",
                "xgSO2_mf",
                "xgH2S_mf",
                "xgCO2_mf",
                "xgCO_mf",
                "xgCH4_mf",
                "xgOCS_mf",
                "xgX_mf",
                "xgC_S_mf",
                "yO2",
                "yH2",
                "yH2O",
                "yS2",
                "ySO2",
                "yH2S",
                "yCO2",
                "yCO",
                "yCH4",
                "yOCS",
                "yX",
                "M_m_SO",
                "M_m_ox",
                "C_H2O_mf_bar",
                "C_H2_ppm_bar",
                "C_CO2T_mf_bar",
                "C_CO_ppm_bar",
                "C_CH4_ppm_bar",
                "C_S_ppm",
                "C_SO4_ppm_bar",
                "C_H2S_ppm_bar",
                "C_X_ppm_bar",
                "KHOg",
                "KHOSg",
                "KCOg",
                "KCOHg",
                "KOCSg",
                "KSOg",
                "KSOg2",
                "KHOm",
                "KCOm",
                "KCOs",
                "density_gcm3",
            ]
        ]
    )
    results_values = pd.DataFrame(
        [
            [
                mg.fO22Dbuffer(PT, mdv.f_O2(PT, melt_wf, models), "NNO", models),
                mg.fO22Dbuffer(PT, mdv.f_O2(PT, melt_wf, models), "FMQ", models),
                mdv.f_O2(PT, melt_wf, models),
                mg.f_H2(PT, melt_wf, models),
                mg.f_H2O(PT, melt_wf, models),
                mg.f_S2(PT, melt_wf, models),
                mg.f_SO2(PT, melt_wf, models),
                mg.f_H2S(PT, melt_wf, models),
                mg.f_CO2(PT, melt_wf, models),
                mg.f_CO(PT, melt_wf, models),
                mg.f_CH4(PT, melt_wf, models),
                mg.f_OCS(PT, melt_wf, models),
                mg.f_X(PT, melt_wf, models),
                mg.p_O2(PT, melt_wf, models),
                mg.p_H2(PT, melt_wf, models),
                mg.p_H2O(PT, melt_wf, models),
                mg.p_S2(PT, melt_wf, models),
                mg.p_SO2(PT, melt_wf, models),
                mg.p_H2S(PT, melt_wf, models),
                mg.p_CO2(PT, melt_wf, models),
                mg.p_CO(PT, melt_wf, models),
                mg.p_CH4(PT, melt_wf, models),
                mg.p_OCS(PT, melt_wf, models),
                mg.p_X(PT, melt_wf, models),
                mg.xg_O2(PT, melt_wf, models),
                mg.xg_H2(PT, melt_wf, models),
                mg.xg_H2O(PT, melt_wf, models),
                mg.xg_S2(PT, melt_wf, models),
                mg.xg_SO2(PT, melt_wf, models),
                mg.xg_H2S(PT, melt_wf, models),
                mg.xg_CO2(PT, melt_wf, models),
                mg.xg_CO(PT, melt_wf, models),
                mg.xg_CH4(PT, melt_wf, models),
                mg.xg_OCS(PT, melt_wf, models),
                mg.xg_X(PT, melt_wf, models),
                mg.gas_CS(PT, melt_wf, models),
                mdv.y_O2(PT, models),
                mdv.y_H2(PT, models),
                mdv.y_H2O(PT, models),
                mdv.y_S2(PT, models),
                mdv.y_SO2(PT, models),
                mdv.y_H2S(PT, models),
                mdv.y_CO2(PT, models),
                mdv.y_CO(PT, models),
                mdv.y_CH4(PT, models),
                mdv.y_OCS(PT, models),
                mdv.y_X(PT, models),
                mg.M_m_SO(melt_wf),
                mg.M_m_ox(melt_wf, models),
                mdv.C_H2O(PT, melt_wf, models),
                mdv.C_H2(PT, melt_wf, models),
                mdv.C_CO3(PT, melt_wf, models),
                mdv.C_CO(PT, melt_wf, models),
                mdv.C_CH4(PT, melt_wf, models),
                mdv.C_S(PT, melt_wf, models),
                mdv.C_SO4(PT, melt_wf, models),
                mdv.C_H2S(PT, melt_wf, models),
                mdv.C_X(PT, melt_wf, models),
                mdv.KHOg(PT, models),
                mdv.KHOSg(PT, models),
                mdv.KCOg(PT, models),
                mdv.KCOHg(PT, models),
                mdv.KOCSg(PT, models),
                mdv.KOSg(PT, models),
                mdv.KOSg2(PT, models),
                mdv.KHOm(PT, melt_wf, models),
                mdv.KCOm(PT, melt_wf, models),
                mdv.KCOs(PT, models),
                mdv.melt_density(PT, melt_wf, models),
            ]
        ]
    )
    return results_headers, results_values


# headers for open system degassing all gas
def results_table_open_all_gas():
    """Creates DataFrame of headers for cumulative gas composition

    Returns:
        pandas.DataFrame: Headers for cumulative gas composition
    """
    results_headers = pd.DataFrame(
        [
            [
                "xgO2_all_mf",
                "xgH2_all_mf",
                "xgH2O_all_mf",
                "xgS2_all_mf",
                "xgSO2_all_mf",
                "xgH2S_all_mf",
                "xgCO2_all_mf",
                "xgCO_all_mf",
                "xgCH4_all_mf",
                "xgOCS_all_mf",
                "xgX_all_mf",
                "xgC_S_all_mf",
            ]
        ]
    )
    return results_headers


# saturation conditions
def results_table_sat(sulf_sat_result, PT, melt_wf, models):
    """Creates DataFrame of headers and values for sulfur and graphite saturation
    results.

    Args:
        sulf_sat_result (dict): Sulfur saturation results
        PT (dict): Pressure in bars as "P" and temperature in 'C as "T"
        melt_wf (dict): Melt composition (SiO2, TiO2, etc. including volatiles)
        models (pandas.DataFrame): Model options

    Returns:
        pandas.DataFrame: Headers and values for sulfur and graphite saturation results
    """
    results_headers = pd.DataFrame(
        [
            [
                "SCSS_ppm",
                "sulfide saturated",
                "SCAS_ppm",
                "anhydrite saturated",
                "ST melt if sat",
                "graphite saturated",
            ]
        ]
    )
    results_values = pd.DataFrame(
        [
            [
                sulf_sat_result["SCSS"],
                sulf_sat_result["sulfide_sat"],
                sulf_sat_result["SCAS"],
                sulf_sat_result["sulfate_sat"],
                sulf_sat_result["ST"],
                c.graphite_saturation(PT, melt_wf, models),
            ]
        ]
    )
    return results_headers, results_values


# isotopes
# WORK IN PROGRESS
def results_table_isotope_R(
    R, R_all_species_S, R_m_g_S, R_all_species_C, R_m_g_C, R_all_species_H, R_m_g_H
):
    headers = pd.DataFrame(
        [
            [
                "R_ST",
                "R_S_m",
                "R_S_g",
                "R_S_S2-",
                "R_S_S2",
                "R_S_OCS",
                "R_S_H2S",
                "R_S_SO2",
                "R_S_S6+",
                "R_S_H2Smol",
                "a_S_g_m",
                "R_CT",
                "R_C_m",
                "R_C_g",
                "R_C_CO2",
                "R_C_CO",
                "R_C_CH4",
                "R_C_OCS",
                "R_C_COmol",
                "R_C_CH4mol",
                "R_C_CO2mol",
                "R_C_CO32-",
                "a_C_g_m",
                "R_HT",
                "R_H_m",
                "R_H_g",
                "R_H_H2O",
                "R_H_H2",
                "R_H_CH4",
                "R_H_H2S",
                "R_H_H2mol",
                "R_H_CH4mol",
                "R_H_H2Smol",
                "R_H_H2Omol",
                "R_H_OH-",
                "a_H_g_m",
            ]
        ]
    )
    values = pd.DataFrame(
        [
            [
                R["S"],
                R_m_g_S["R_m"],
                R_m_g_S["R_g"],
                R_all_species_S["A"],
                R_all_species_S["B"],
                R_all_species_S["C"],
                R_all_species_S["D"],
                R_all_species_S["E"],
                R_all_species_S["F"],
                R_all_species_S["G"],
                R_m_g_S["R_g"] / R_m_g_S["R_m"],
                R["C"],
                R_m_g_C["R_m"],
                R_m_g_C["R_g"],
                R_all_species_C["A"],
                R_all_species_C["B"],
                R_all_species_C["C"],
                R_all_species_C["D"],
                R_all_species_C["E"],
                R_all_species_C["F"],
                R_all_species_C["G"],
                R_all_species_C["H"],
                R_m_g_C["R_g"] / R_m_g_C["R_m"],
                R["H"],
                R_m_g_H["R_m"],
                R_m_g_H["R_g"],
                R_all_species_H["A"],
                R_all_species_H["B"],
                R_all_species_H["C"],
                R_all_species_H["D"],
                R_all_species_H["E"],
                R_all_species_H["F"],
                R_all_species_H["G"],
                R_all_species_H["H"],
                R_all_species_H["I"],
                R_m_g_H["R_g"] / R_m_g_H["R_m"],
            ]
        ]
    )
    return headers, values


# def results_table_isotope_a_D():
# return headers, values
# WORK IN PROGRESS
def results_table_isotope_d(
    R, R_all_species_S, R_m_g_S, R_all_species_C, R_m_g_C, R_all_species_H, R_m_g_H
):
    headers = pd.DataFrame(
        [
            [
                "d_ST",
                "d_S_m",
                "d_S_g",
                "d_S_S2-",
                "d_S_S2",
                "d_S_OCS",
                "d_S_H2S",
                "d_S_SO2",
                "d_S_S6+",
                "d_S_H2Smol",
                "D_S_g_m",
                "d_CT",
                "d_C_m",
                "d_C_g",
                "d_C_CO2",
                "d_C_CO",
                "d_C_CH4",
                "d_C_OCS",
                "d_C_COmol",
                "d_C_CH4mol",
                "d_C_CO2mol",
                "d_C_CO32-",
                "D_C_g_m",
                "d_HT",
                "d_H_m",
                "d_H_g",
                "d_H_H2O",
                "d_H_H2",
                "d_H_CH4",
                "d_H_H2S",
                "d_H_H2mol",
                "d_H_CH4mol",
                "d_H_H2Smol",
                "d_H_H2Omol",
                "d_H_OH-",
                "D_H_g_m",
            ]
        ]
    )
    values = pd.DataFrame(
        [
            [
                iso.ratio2delta("VCDT", 34, "S", R["S"]),
                iso.ratio2delta("VCDT", 34, "S", R_m_g_S["R_m"]),
                iso.ratio2delta("VCDT", 34, "S", R_m_g_S["R_g"]),
                iso.ratio2delta("VCDT", 34, "S", R_all_species_S["A"]),
                iso.ratio2delta("VCDT", 34, "S", R_all_species_S["B"]),
                iso.ratio2delta("VCDT", 34, "S", R_all_species_S["C"]),
                iso.ratio2delta("VCDT", 34, "S", R_all_species_S["D"]),
                iso.ratio2delta("VCDT", 34, "S", R_all_species_S["E"]),
                iso.ratio2delta("VCDT", 34, "S", R_all_species_S["F"]),
                iso.ratio2delta("VCDT", 34, "S", R_all_species_S["G"]),
                iso.alpha2Delta((R_m_g_S["R_g"] / R_m_g_S["R_m"])),
                iso.ratio2delta("VPDB", 13, "C", R["C"]),
                iso.ratio2delta("VPDB", 13, "C", R_m_g_C["R_m"]),
                iso.ratio2delta("VPDB", 13, "C", R_m_g_C["R_g"]),
                iso.ratio2delta("VPDB", 13, "C", R_all_species_C["A"]),
                iso.ratio2delta("VPDB", 13, "C", R_all_species_C["B"]),
                iso.ratio2delta("VPDB", 13, "C", R_all_species_C["C"]),
                iso.ratio2delta("VPDB", 13, "C", R_all_species_C["D"]),
                iso.ratio2delta("VPDB", 13, "C", R_all_species_C["E"]),
                iso.ratio2delta("VPDB", 13, "C", R_all_species_C["F"]),
                iso.ratio2delta("VPDB", 13, "C", R_all_species_C["G"]),
                iso.ratio2delta("VPDB", 13, "C", R_all_species_C["H"]),
                iso.alpha2Delta((R_m_g_C["R_g"] / R_m_g_C["R_m"])),
                iso.ratio2delta("VSMOW", 2, "H", R["H"]),
                iso.ratio2delta("VSMOW", 2, "H", R_m_g_H["R_m"]),
                iso.ratio2delta("VSMOW", 2, "H", R_m_g_H["R_g"]),
                iso.ratio2delta("VSMOW", 2, "H", R_all_species_H["A"]),
                iso.ratio2delta("VSMOW", 2, "H", R_all_species_H["B"]),
                iso.ratio2delta("VSMOW", 2, "H", R_all_species_H["C"]),
                iso.ratio2delta("VSMOW", 2, "H", R_all_species_H["D"]),
                iso.ratio2delta("VSMOW", 2, "H", R_all_species_H["E"]),
                iso.ratio2delta("VSMOW", 2, "H", R_all_species_H["F"]),
                iso.ratio2delta("VSMOW", 2, "H", R_all_species_H["G"]),
                iso.ratio2delta("VSMOW", 2, "H", R_all_species_H["H"]),
                iso.ratio2delta("VSMOW", 2, "H", R_all_species_H["I"]),
                iso.alpha2Delta((R_m_g_H["R_g"] / R_m_g_H["R_m"])),
            ]
        ]
    )
    return headers, values


###############################
# options from setup file #####
###############################
def options_from_setup(run, models, setup):
    """
    # WORK IN PROGRESS # Allows model options to be read from the setup file rather than
    models file.


    Parameters
    ----------
    run: int
        Integer of the row in the setup file to read from (note the first row under the
        headers is row 0).
    models: pandas.DataFrame
        Model options
    setup: pandas.DataFrame
        Melt compositions to be used, require header using the same labels as row labels
        from models file if you want to use that option.

    Returns
    -------
    pandas.DataFrame
        Models options with the options updated from the setup file.
    """
    if models.loc["setup", "option"] == "False":
        return models
    elif models.loc["setup", "option"] == "True":
        # species
        if models.loc["COH_species", "option"] == "setup":
            models.loc["COH_species", "option"] = setup.loc[run, "COH_species"]
        if models.loc["H2S_m", "option"] == "setup":
            models.loc["H2S_m", "option"] = setup.loc[run, "H2S_m"]
        if models.loc["species X", "option"] == "setup":
            models.loc["species X", "option"] = setup.loc[run, "species X"]
        if models.loc["Hspeciation", "option"] == "setup":
            models.loc["Hspeciation", "option"] = setup.loc[run, "Hspeciation"]
        # oxygen fugacity
        if models.loc["fO2", "option"] == "setup":
            models.loc["fO2", "option"] = setup.loc[run, "fO2"]
        if models.loc["NNObuffer", "option"] == "setup":
            models.loc["NNObuffer", "option"] = setup.loc[run, "NNObuffer"]
        if models.loc["FMQbuffer", "option"] == "setup":
            models.loc["FMQbuffer", "option"] = setup.loc[run, "FMQbuffer"]
        # solubility constants
        if models.loc["carbon dioxide", "option"] == "setup":
            models.loc["carbon dioxide", "option"] = setup.loc[run, "carbon dioxide"]
        if models.loc["water", "option"] == "setup":
            models.loc["water", "option"] = setup.loc[run, "water"]
        if models.loc["hydrogen", "option"] == "setup":
            models.loc["hydrogen", "option"] = setup.loc[run, "hydrogen"]
        if models.loc["sulfide", "option"] == "setup":
            models.loc["sulfide", "option"] = setup.loc[run, "sulfide"]
        if models.loc["sulfate", "option"] == "setup":
            models.loc["sulfate", "option"] = setup.loc[run, "sulfate"]
        if models.loc["hydrogen sulfide", "option"] == "setup":
            models.loc["hydrogen sulfide", "option"] = setup.loc[
                run, "hydrogen sulfide"
            ]
        if models.loc["methane", "option"] == "setup":
            models.loc["methane", "option"] = setup.loc[run, "methane"]
        if models.loc["carbon monoxide", "option"] == "setup":
            models.loc["carbon monoxide", "option"] = setup.loc[run, "carbon monoxide"]
        if models.loc["species X solubility", "option"] == "setup":
            models.loc["species X solubility", "option"] = setup.loc[
                run, "species X solubility"
            ]
        if models.loc["Cspeccomp", "option"] == "setup":
            models.loc["Cspeccomp", "option"] = setup.loc[run, "Cspeccomp"]
        if models.loc["Hspeccomp", "option"] == "setup":
            models.loc["Hspeccomp", "option"] = setup.loc[run, "Hspeccomp"]
        # saturation conditions
        if models.loc["SCSS", "option"] == "setup":
            models.loc["SCSS", "option"] = setup.loc[run, "SCSS"]
        if models.loc["SCAS", "option"] == "setup":
            models.loc["SCAS", "option"] = setup.loc[run, "SCAS"]
        if models.loc["sulfur_saturation", "option"] == "setup":
            models.loc["sulfur_saturation", "option"] = setup.loc[
                run, "sulfur_saturation"
            ]
        if models.loc["sulfur_is_sat", "option"] == "setup":
            models.loc["sulfur_is_sat", "option"] = setup.loc[run, "sulfur_is_sat"]
        if models.loc["graphite_saturation", "option"] == "setup":
            models.loc["graphite_saturation", "option"] = setup.loc[
                run, "graphite_saturation"
            ]
        # fugacity coefficients
        if models.loc["ideal_gas", "option"] == "setup":
            models.loc["ideal_gas", "option"] = setup.loc[run, "ideal_gas"]
        if models.loc["y_CO2", "option"] == "setup":
            models.loc["y_CO2", "option"] = setup.loc[run, "y_CO2", "option"]
        if models.loc["y_SO2", "option"] == "setup":
            models.loc["y_SO2", "option"] = setup.loc[run, "y_SO2", "option"]
        if models.loc["y_H2S", "option"] == "setup":
            models.loc["y_H2S", "option"] = setup.loc[run, "y_H2S", "option"]
        if models.loc["y_H2", "option"] == "setup":
            models.loc["y_H2", "option"] = setup.loc[run, "y_H2", "option"]
        if models.loc["y_O2", "option"] == "setup":
            models.loc["y_O2", "option"] = setup.loc[run, "y_O2", "option"]
        if models.loc["y_S2", "option"] == "setup":
            models.loc["y_S2", "option"] = setup.loc[run, "y_S2", "option"]
        if models.loc["y_CO", "option"] == "setup":
            models.loc["y_CO", "option"] = setup.loc[run, "y_CO", "option"]
        if models.loc["y_CH4", "option"] == "setup":
            models.loc["y_CH4", "option"] = setup.loc[run, "y_CH4", "option"]
        if models.loc["y_H2O", "option"] == "setup":
            models.loc["y_H2O", "option"] = setup.loc[run, "y_H2O", "option"]
        if models.loc["y_OCS", "option"] == "setup":
            models.loc["y_OCS", "option"] = setup.loc[run, "y_OCS", "option"]
        if models.loc["y_X", "option"] == "setup":
            models.loc["y_X", "option"] = setup.loc[run, "y_X", "option"]
        # equilibrium constants
        if models.loc["KHOg", "option"] == "setup":
            models.loc["KHOg", "option"] = setup.loc[run, "KHOg", "option"]
        if models.loc["KHOSg", "option"] == "setup":
            models.loc["KHOSg", "option"] = setup.loc[run, "KHOSg", "option"]
        if models.loc["KOSg", "option"] == "setup":
            (models.loc["KOSg", "option"],) = setup.loc[run, "KOSg", "option"]
        if models.loc["KOSg2", "option"] == "setup":
            models.loc["KOSg2", "option"] = setup.loc[run, "KOSg2", "option"]
        if models.loc["KCOg", "option"] == "setup":
            models.loc["KCOg", "option"] = setup.loc[run, "KCOg", "option"]
        if models.loc["KCOHg", "option"] == "setup":
            models.loc["KCOHg", "option"] = setup.loc[run, "KCOHg", "option"]
        if models.loc["KOCSg", "option"] == "setup":
            models.loc["KOCSg", "option"] = setup.loc[run, "KOCSg", "option"]
        if models.loc["KCOs", "option"] == "setup":
            models.loc["KCOs", "option"] = setup.loc[run, "KCOs", "option"]
        if models.loc["carbonylsulfide", "option"] == "setup":
            models.loc["carbonylsulfide", "option"] = setup.loc[
                run, "carbonylsulfide", "option"
            ]
        # other
        if models.loc["density", "option"] == "setup":
            models.loc["density", "option"] = setup.loc[run, "density", "option"]
        return models


##################################################
# calculate the pressure of vapor saturation #####
##################################################
def calc_Pvsat(
    setup,
    models=mdv.default_models,
    first_row=0,
    last_row=None,
    p_tol=1.0e-1,
    nr_step=1.0,
    nr_tol=1.0e-9,
):
    """Calculates the pressure of vapor saturation for multiple melt compositions given
    volatile-free melt composition, volatile content, temperature, and an fO2 estimate.

    Args:
        setup (pandas.DataFrame): Melt compositions to be used, requires following headers: Sample; T_C; DNNO or DFMQ or logfO2 or (Fe2O3 and FeO) or Fe3FeT or S6ST; SiO2, TiO2, Al2O3, (Fe2O3T or FeOT unless Fe2O3 and FeO given), MnO, MgO, CaO, Na2O, K2O, P2O5; H2O and/or CO2ppm and/or STppm and/or Xppm. Note: concentrations (unless otherwise stated) are in wt%
        models (_type_pandas.DataFrame, optional): Model options. Defaults to mdv.default_models.
        first_row (int, optional): Integer of the first row in the setup file to run (note the first row under the headers is row 0). Defaults to 0.
        last_row (float, optional): Integer of the last row in the setup file to run (note the first row under the headers is row 0). Defaults to None.
        p_tol (float, optional): Required tolerance for convergence of Pvsat in bars. Defaults to 1.0e-1.
        nr_step (float, optional): Step size for Newton-Raphson solver for melt speciation (this can be made smaller if there are problems with convergence.) Defaults to 1.0.
        nr_tol (float, optional): Tolerance for the Newton-Raphson solver for melt speciation in weight fraction (this can be made larger if there are problems with convergence.) Defaults to 1.0e-9.

    Returns:
        pandas.DataFrame: Results of pressure of vapor saturation calculation


    Outputs
    -------
    results_saturation_pressures: csv file (if output csv = yes in models)

    """
    if last_row is None:
        last_row = len(setup)

    for n in range(
        first_row, last_row, 1
    ):  # n is number of rows of data in conditions file
        run = n
        PT = {"T": setup.loc[run, "T_C"]}
        melt_wf_i = mg.melt_comp(run, setup)
        melt_wf = mg.melt_comp(run, setup)

        # check if any options need to be read from the setup file rather than the
        # models file
        models = options_from_setup(run, models, setup)

        # calculate Pvsat assuming only H2O CO2 in vapour and melt
        # if setup.loc[run,"Fe3FeT"] > 0.:
        #    melt_wf['Fe3FeT'] = setup.loc[run,"Fe3FeT"]
        # else:
        #    melt_wf['Fe3FeT'] = 0.
        P_sat_H2O_CO2_only, P_sat_H2O_CO2_result = c.P_sat_H2O_CO2(
            PT, melt_wf, models, p_tol, nr_step, nr_tol
        )

        if models.loc["calc_sat", "option"] == "fO2_fX":
            P_sat_fO2_fS2_result = c.P_sat_fO2_fS2(PT, melt_wf, models, p_tol)
            PT["P"] = P_sat_fO2_fS2_result["P_tot"]
        else:
            wm_ST = melt_wf["ST"]
        melt_wf["ST"] = wm_ST

        # if models.loc["bulk_composition", "option"] == "melt-only":
        #    bulk_wf = {
        #        "H": (2.0 * mdv.species.loc["H", "M"] * melt_wf["H2OT"])
        #        / mdv.species.loc["H2O", "M"],
        #        "C": (mdv.species.loc["C", "M"] * melt_wf["CO2"])
        #        / mdv.species.loc["CO2", "M"],
        #        "S": wm_ST,
        #        "X": wm_X,
        #    }
        # else:
        #    raise TypeError("This is not currently possible")
        if models.loc["sulfur_is_sat", "option"] == "yes":
            if melt_wf["XT"] > 0.0:
                raise TypeError("This is not currently possible")
            P_sat_, conc, frac = c.fO2_P_VSA(
                PT, melt_wf, models, nr_step, nr_tol, p_tol
            )
        elif models.loc["sulfur_saturation", "option"] == "False":
            P_sat_, conc, frac = c.P_sat(PT, melt_wf, models, p_tol, nr_step, nr_tol)
        elif models.loc["sulfur_saturation", "option"] == "True":
            if melt_wf["XT"] > 0.0:
                raise TypeError("This is not currently possible")
            P_sat_, conc, frac = c.P_VSA(PT, melt_wf, models, nr_step, nr_tol, p_tol)
        PT["P"] = P_sat_
        melt_wf["H2OT"] = conc["wm_H2O"]
        melt_wf["CO2"] = conc["wm_CO2"]
        melt_wf["S2-"] = conc["wm_S2m"]
        melt_wf["Fe3FeT"] = conc["Fe3FeT"]
        # if models.loc["sulfur_is_sat","option"] == "yes":
        #    melt_wf["Fe3FeT"] = frac["Fe3FeT"]
        # else:
        #    melt_wf["Fe3FeT"] = mg.Fe3FeT_i(PT,melt_wf,models)

        sulf_sat_result = c.sulfur_saturation(PT, melt_wf, models)
        # gas_mf = {"O2":mg.xg_O2(PT,melt_wf,models),"CO":mg.xg_CO(PT,melt_wf,models),
        # "CO2":mg.xg_CO2(PT,melt_wf,models),"H2":mg.xg_H2(PT,melt_wf,models),
        # "H2O":mg.xg_H2O(PT,melt_wf,models),"CH4":mg.xg_CH4(PT,melt_wf,models),
        # "S2":mg.xg_S2(PT,melt_wf,models),"SO2":mg.xg_SO2(PT,melt_wf,models),
        # "H2S":mg.xg_H2S(PT,melt_wf,models),"OCS":mg.xg_OCS(PT,melt_wf,models),
        # "X":mg.xg_X(PT,melt_wf,models),"Xg_t":mg.Xg_tot(PT,melt_wf,models),"wt_g":0.}
        melt_comp = mg.melt_normalise_wf(melt_wf, "yes", "no")

        # create results
        results_headers_table_sample_name, results_values_table_sample_name = (
            results_table_sample_name(setup, run)
        )
        results_headers_table_melt_comp_etc, results_values_table_melt_comp_etc = (
            results_table_melt_comp_etc(PT, melt_comp, conc, frac, melt_wf)
        )
        results_headers_table_model_options, results_values_table_model_options = (
            results_table_model_options(models)
        )
        (
            results_headers_table_f_p_xg_y_M_C_K_d,
            results_values_table_f_p_xg_y_M_C_K_d,
        ) = results_table_f_p_xg_y_M_C_K_d(PT, melt_wf, models)
        results_headers_table_sat, results_values_table_sat = results_table_sat(
            sulf_sat_result, PT, melt_wf, models
        )
        results_headers_table_melt_vol = (
            results_table_melt_vol()
        )  # "H2OT-eq_wtpc","CO2T-eq_ppmw","ST_ppmw","X_ppmw"
        results_values_table_melt_vol = pd.DataFrame(
            [
                [
                    melt_wf_i["H2OT"] * 100.0,
                    melt_wf_i["CO2"] * 1000000.0,
                    melt_wf_i["ST"] * 1000000.0,
                    melt_wf_i["XT"] * 1000000.0,
                ]
            ]
        )
        results_headers_table_H2OCO2only = pd.DataFrame(
            [
                [
                    "Pvsat (H2O CO2 only)",
                    "xg_H2O (H2O CO2 only)",
                    "xg_CO2 (H2O CO2 only)",
                    "f_H2O (H2O CO2 only)",
                    "f_CO2 (H2O CO2 only)",
                    "p_H2O (H2O CO2 only)",
                    "p_CO2 (H2O CO2 only)",
                    "Pvsat_diff_bar",
                ]
            ]
        )
        results_values_table_H2OCO2only = pd.DataFrame(
            [
                [
                    P_sat_H2O_CO2_only,
                    P_sat_H2O_CO2_result["xg_H2O"],
                    P_sat_H2O_CO2_result["xg_CO2"],
                    P_sat_H2O_CO2_result["f_H2O"],
                    P_sat_H2O_CO2_result["f_CO2"],
                    P_sat_H2O_CO2_result["p_H2O"],
                    P_sat_H2O_CO2_result["p_CO2"],
                    (P_sat_H2O_CO2_only - PT["P"]),
                ]
            ]
        )
        results_headers = pd.concat(
            [
                results_headers_table_sample_name,
                results_headers_table_melt_comp_etc,
                results_headers_table_melt_vol,
                results_headers_table_sat,
                results_headers_table_H2OCO2only,
                results_headers_table_f_p_xg_y_M_C_K_d,
                results_headers_table_model_options,
            ],
            axis=1,
        )
        results1 = pd.concat(
            [
                results_values_table_sample_name,
                results_values_table_melt_comp_etc,
                results_values_table_melt_vol,
                results_values_table_sat,
                results_values_table_H2OCO2only,
                results_values_table_f_p_xg_y_M_C_K_d,
                results_values_table_model_options,
            ],
            axis=1,
        )

        if n == first_row:
            results = pd.concat([results_headers, results1])
        else:
            results = pd.concat([results, results1])

        if models.loc["print status", "option"] == "True":
            print(n, setup.loc[run, "Sample"], PT["P"])

    results.columns = results.iloc[0]
    results = results[1:]
    results.reset_index(drop=True, inplace=True)
    if models.loc["output csv", "option"] == "True":
        results.to_csv("results_saturation_pressures.csv", index=False, header=True)

    return results


###################################
# calcuate re/degassing paths #####
###################################
def calc_gassing(
    setup,
    models=mdv.default_models,
    run=0,
    nr_step=1.0,
    nr_tol=1.0e-9,
    dp_step="auto",
    psat_tol=0.1,
    dwtg=1.0e-6,
    i_nr_step=1.0e-1,
    i_nr_tol=1.0e-9,
    nr_step_eq=1.0,
    suppress_warnings=True,
):
    """Calculates the pressure of vapor saturation for multiple melt compositions given
    volatile-free melt composition, volatile content, temperature, and an fO2 estimate.

    Args:
        setup (pandas.DataFrame): Melt composition to be used, requires following headers (notes in [] are not part of the headers): Sample; T_C; DNNO or DFMQ or logfO2 or (Fe2O3 and FeO) or Fe3FeT or S6ST [at initial pressure]; SiO2, TiO2, Al2O3, (Fe2O3T or FeOT unless Fe2O3 and FeO given), MnO, MgO, CaO, Na2O, K2O, P2O5 [concentrations are in wt%]; (H2O and/or CO2ppm and/or STppm and/or Xppm) [concentration of H2O in wt%]; final_P [IF regassing, pressure calculation stops at in bars]; wt_g [IF starting from given pressure and gas is present, can specifiy the gas present in wt%]; initial_CO2wtpc [IF starting from given pressure and gas is present, can specifiy initial composition using initial CO2 dissolved in the melt in wt%].
        models (pandas.DataFrame, optional): Model options. Defaults to mdv.default_models.
        run (int, optional): Integer of the row in the setup file to run (note the first row under the headers is row 0). Defaults to 0.
        nr_step (float, optional): Step size for Newton-Raphson solver for melt speciation (typically 1 is fine, but this can be made smaller if there are problems with convergence). Defaults to 1.0.
        nr_tol (float, optional): Tolerance for the Newton-Raphson solver for melt speciation in weight fraction (can be increased if there are problems with convergence). Defaults to 1.0e-9.
        dp_step (float, optional): Pressure step size for gassing calculation in bars. Defaults to "auto".
        psat_tol (float, optional): Required tolerance for convergence of Pvsat in bars. Defaults to 0.1.
        dwtg (float, optional):  Amount of gas to add at each step if regassing in an open-system in wt fraction total system. Defaults to 1.0e-6.
        i_nr_step (float, optional): Step-size for newton-raphson convergence for isotopes (can be increased if there are problems with convergence). Defaults to 1.0e-1.
        i_nr_tol (float, optional): Tolerance for newton-raphson convergence for isotopes (can be increased if there are problems with convergence). Defaults to 1.0-9.
        nr_step_eq (float, optional): Step-size for new-raphson solver for isotopes. Defaults to 1.0.
        suppress_warnings (bool, optional): Suppress runtime warnings. Defaults to True.

    Returns:
        pandas.DataFrame: Results of degassing calculation.


    Outputs
    -------
    If output csv = yes in models results_gassing_chemistry: csv file
    """

    if models.loc["print status", "option"] == "True":
        print(setup.loc[run, "Sample"])

    # check if any options need to be read from the setup file rather than the models
    # file
    models = options_from_setup(run, models, setup)

    if models.loc["fO2", "option"] != "Kress91A":
        raise TypeError(
            "Change 'fO2' option in models to 'Kress91A': other fO2 options are not currently supported"  # noqa
        )

    # set T and volatile composition of the melt
    PT = {"T": setup.loc[run, "T_C"]}
    melt_wf = mg.melt_comp(run, setup)
    melt_wf_i = mg.melt_comp(run, setup)

    # Calculate saturation pressure for composition given in setup file
    if models.loc["COH_species", "option"] == "H2O-CO2 only":
        P_sat_, P_sat_H2O_CO2_result = c.P_sat_H2O_CO2(
            PT, melt_wf, models, psat_tol, nr_step, nr_tol
        )
        wm_H2Omol_, wm_OH_ = mg.wm_H2Omol_OH(PT, melt_wf, models)
        wm_CO2carb_, wm_CO2mol_ = mg.wm_CO32_CO2mol(PT, melt_wf, models)
        conc = {
            "wm_H2O": P_sat_H2O_CO2_result["wm_H2O"],
            "wm_CO2": P_sat_H2O_CO2_result["wm_CO2"],
            "wm_OH": wm_OH_,
            "wm_H2Omol": wm_H2Omol_,
            "wm_CO2mol": wm_CO2mol_,
            "wm_CO2carb": wm_CO2carb_,
            "wm_H2": 0.0,
            "wm_CO": 0.0,
            "wm_CH4": 0.0,
            "wm_H2S": 0.0,
            "wm_S2m": 0.0,
            "wm_S6p": 0.0,
            "ST": 0.0,
            "Fe3FeT": melt_wf["Fe3FeT_i"],
        }
        frac = c.melt_species_ratios(conc)
    else:
        P_sat_, conc, frac = c.P_sat(PT, melt_wf, models, psat_tol, nr_step, nr_tol)
    PT["P"] = P_sat_
    if models.loc["print status", "option"] == "True":
        print("T=", PT["T"], "P=", PT["P"], datetime.datetime.now())

    # update melt composition at saturation pressure, check for sulfur saturation, and
    # calculate some things
    melt_wf["H2OT"] = conc["wm_H2O"]
    melt_wf["CO2"] = conc["wm_CO2"]
    melt_wf["CO"] = conc["wm_CO"]
    melt_wf["CH4"] = conc["wm_CH4"]
    melt_wf["H2"] = conc["wm_H2"]
    melt_wf["S2-"] = conc["wm_S2m"]
    melt_wf["S6+"] = conc["wm_S6p"]
    melt_wf["H2S"] = conc["wm_H2S"]
    melt_wf["Fe3FeT"] = conc["Fe3FeT"]
    melt_wf["S6ST"] = mg.S6ST(PT, melt_wf, models)
    sulf_sat_result = c.sulfur_saturation(PT, melt_wf, models)
    wm_CO2eq, wm_H2Oeq = mg.melt_H2O_CO2_eq(melt_wf)
    melt_comp = mg.melt_normalise_wf(melt_wf, "yes", "no")

    # Set bulk composition
    bulk_comp = c.bulk_composition(run, PT, melt_wf, setup, models)
    bulk_wf = {
        "C": bulk_comp["wt_C"],
        "H": bulk_comp["wt_H"],
        "O": bulk_comp["wt_O"],
        "S": bulk_comp["wt_S"],
        "Fe": bulk_comp["wt_Fe"],
        "Wt": bulk_comp["Wt"],
        "X": bulk_comp["wt_X"],
    }

    # set system and initial guesses
    system = eq.set_system(melt_wf, models)
    guesses = eq.initial_guesses(run, PT, melt_wf, setup, models, system)

    # create results
    results_headers_table_sample_name, results_values_table_sample_name = (
        results_table_sample_name(setup, run)
    )
    results_headers_table_melt_comp_etc, results_values_table_melt_comp_etc = (
        results_table_melt_comp_etc(PT, melt_comp, conc, frac, melt_wf)
    )
    results_headers_table_model_options, results_values_table_model_options = (
        results_table_model_options(models)
    )
    results_headers_table_f_p_xg_y_M_C_K_d, results_values_table_f_p_xg_y_M_C_K_d = (
        results_table_f_p_xg_y_M_C_K_d(PT, melt_wf, models)
    )
    results_headers_table_sat, results_values_table_sat = results_table_sat(
        sulf_sat_result, PT, melt_wf, models
    )
    results_headers_table_melt_vol = (
        results_table_melt_vol()
    )  # "H2OT-eq_wtpc","CO2T-eq_ppmw","ST_ppmw","X_ppmw"
    results_values_table_melt_vol = pd.DataFrame(
        [
            [
                melt_wf_i["H2OT"] * 100.0,
                melt_wf_i["CO2"] * 1000000.0,
                melt_wf_i["ST"] * 1000000.0,
                melt_wf_i["XT"] * 1000000.0,
            ]
        ]
    )
    results_headers_table_wtg_etc = pd.DataFrame(
        [
            [
                "wt_g_wtpc",
                "wt_g_O_wtf",
                "wt_g_C_wtf",
                "wt_g_H_wtf",
                "wt_g_S_wtf",
                "wt_g_X_wtf",
                "wt_O_wtpc",
                "wt_C_wtpc",
                "wt_H_wtpc",
                "wt_S_wtpc",
                "wt_X_wtpc",
                "Solving species",
                "mass balance C",
                "mass balance O",
                "mass balance H",
                "mass balance S",
            ]
        ]
    )
    results_values_table_wtg_etc = pd.DataFrame(
        [
            [
                bulk_comp["wt_g"] * 100.0,
                "",
                "",
                "",
                "",
                "",
                bulk_wf["O"] * 100.0,
                bulk_wf["C"] * 100.0,
                bulk_wf["H"] * 100.0,
                bulk_wf["S"] * 100.0,
                bulk_wf["X"] * 100.0,
                "",
                "",
                "",
                "",
                "",
            ]
        ]
    )
    if (
        models.loc["gassing_style", "option"] == "open"
        and models.loc["gassing_direction", "option"] == "degas"
    ):
        results_headers_table_open_all_gas = results_table_open_all_gas()
        results_values_table_open_all_gas = pd.DataFrame(
            [
                [
                    mg.xg_O2(PT, melt_wf, models),
                    mg.xg_H2(PT, melt_wf, models),
                    mg.xg_H2O(PT, melt_wf, models),
                    mg.xg_S2(PT, melt_wf, models),
                    mg.xg_SO2(PT, melt_wf, models),
                    mg.xg_H2S(PT, melt_wf, models),
                    mg.xg_CO2(PT, melt_wf, models),
                    mg.xg_CO(PT, melt_wf, models),
                    mg.xg_CH4(PT, melt_wf, models),
                    mg.xg_OCS(PT, melt_wf, models),
                    mg.xg_X(PT, melt_wf, models),
                    mg.gas_CS(PT, melt_wf, models),
                ]
            ]
        )
        results_headers = pd.concat(
            [
                results_headers_table_sample_name,
                results_headers_table_melt_comp_etc,
                results_headers_table_melt_vol,
                results_headers_table_sat,
                results_headers_table_f_p_xg_y_M_C_K_d,
                results_headers_table_wtg_etc,
                results_headers_table_open_all_gas,
                results_headers_table_model_options,
            ],
            axis=1,
        )
        results1 = pd.concat(
            [
                results_values_table_sample_name,
                results_values_table_melt_comp_etc,
                results_values_table_melt_vol,
                results_values_table_sat,
                results_values_table_f_p_xg_y_M_C_K_d,
                results_values_table_wtg_etc,
                results_values_table_open_all_gas,
                results_values_table_model_options,
            ],
            axis=1,
        )
    else:
        results_headers = pd.concat(
            [
                results_headers_table_sample_name,
                results_headers_table_melt_comp_etc,
                results_headers_table_melt_vol,
                results_headers_table_sat,
                results_headers_table_f_p_xg_y_M_C_K_d,
                results_headers_table_wtg_etc,
                results_headers_table_model_options,
            ],
            axis=1,
        )
        results1 = pd.concat(
            [
                results_values_table_sample_name,
                results_values_table_melt_comp_etc,
                results_values_table_melt_vol,
                results_values_table_sat,
                results_values_table_f_p_xg_y_M_C_K_d,
                results_values_table_wtg_etc,
                results_values_table_model_options,
            ],
            axis=1,
        )
    results = pd.concat([results_headers, results1])

    # results for isotope calculations...
    if models.loc["isotopes", "option"] == "yes":
        raise TypeError("This is not currently supported")
        a_H2S_S_, a_SO4_S_, a_S2_S_, a_SO2_S_, a_OCS_S_ = iso.i2s6_S_alphas(PT)
        results_isotopes1 = pd.DataFrame(
            [
                [
                    "P",
                    "T_C",
                    "xg_O2",
                    "xg_CO",
                    "xg_CO2",
                    "xg_H2",
                    "xg_H2O",
                    "xg_CH4",
                    "xg_S2",
                    "xg_SO2",
                    "xg_SO3",
                    "xg_H2S",
                    "xg_OCS",
                    "wt_g",
                    "wm_CO2",
                    "wm_H2O",
                    "wm_H2",
                    "wm_S",
                    "wm_SO3",
                    "wm_ST",
                    "Fe3T",
                    "S6T",
                    "DFMQ",
                    "DNNO",
                    "SCSS",
                    "sulfide sat?",
                    "SCAS",
                    "sulfate sat?",
                    "RS_S2-",
                    "RS_SO42-",
                    "RS_H2S",
                    "RS_SO2",
                    "RS_S2",
                    "R_OCS",
                    "R_m",
                    "R_g",
                    "dS_S2-",
                    "dS_SO42-",
                    "dS_H2S",
                    "dS_SO2",
                    "dS_S2",
                    "dS_OCS",
                    "dS_m",
                    "dS_g",
                    "a_H2S_S2-",
                    "a_SO42-_S2-",
                    "a_S2_S2-",
                    "a_SO2_S2-",
                    "a_OCS_S2-",
                    "a_g_m",
                ]
            ]
        )
        results1 = pd.DataFrame(
            [
                [
                    PT["P"],
                    PT["T"],
                    mg.xg_O2(PT, melt_wf, models),
                    mg.xg_CO(PT, melt_wf, models),
                    mg.xg_CO2(PT, melt_wf, models),
                    mg.xg_H2(PT, melt_wf, models),
                    mg.xg_H2O(PT, melt_wf, models),
                    mg.xg_CH4(PT, melt_wf, models),
                    mg.xg_S2(PT, melt_wf, models),
                    mg.xg_SO2(PT, melt_wf, models),
                    mg.xg_H2S(PT, melt_wf, models),
                    mg.xg_OCS(PT, melt_wf, models),
                    # wt_g_,
                    melt_wf["CO2"],
                    melt_wf["H2OT"],
                    0,
                    (mg.wm_S(PT, melt_wf, models) / 100),
                    (mg.wm_SO3(PT, melt_wf, models) / 100),
                    melt_wf["ST"],
                    melt_wf["Fe3FeT"],
                    mg.S6ST(PT, melt_wf, models),
                    mg.fO22Dbuffer(PT, mdv.f_O2(PT, melt_wf, models), "FMQ"),
                    mg.fO22Dbuffer(PT, mdv.f_O2(PT, melt_wf, models), "NNO"),
                    # SCSS_,
                    # sulfide_sat,
                    # SCAS_,
                    # sulfate_sat,
                    # R_S_S2_,
                    # R_S_SO4_,
                    "",
                    "",
                    "",
                    "",
                    # R_i["S"],
                    "",
                    # ratio2delta("VCDT", R_S_S2_),
                    # ratio2delta("VCDT", R_S_SO4_),
                    "",
                    "",
                    "",
                    "",
                    # ratio2delta("VCDT", R_i["S"]),
                    "",
                    a_H2S_S_,
                    a_SO4_S_,
                    a_S2_S_,
                    a_SO2_S_,
                    a_OCS_S_,
                    "",
                ]
            ]
        )
        results_isotopes = pd.concat([results_isotopes1, results1], ignore_index=True)
        if models.loc["output csv", "option"] == "True":
            results_isotopes.to_csv(
                "results_gassing_isotopes.csv", index=False, header=False
            )

    if dp_step == "auto":
        dp_step_choice = "auto"
        if models.loc["gassing_style", "option"] == "open":
            dp_step = 1.0
        else:
            if PT["P"] > 5000.0:
                dp_step = 500.0
            elif PT["P"] > 200.0:
                dp_step = 100.0
            elif PT["P"] > 50.0:
                dp_step = 10.0
            else:
                dp_step = 1.0
    else:
        dp_step_choice = "user"

    if models.loc["P_variation", "option"] == "polybaric":
        # pressure ranges and options
        starting_P = models.loc["starting_P", "option"]
        if starting_P == "set":
            initial = int(setup.loc[run, "P_bar"])
        else:
            if models.loc["gassing_direction", "option"] == "degas":
                answer = math.floor(PT["P"] / dp_step)
                initial = round(answer * dp_step)
            elif models.loc["gassing_direction", "option"] == "regas":
                answer = math.ceil(PT["P"] / dp_step)
                initial = round(answer * dp_step)
        if models.loc["gassing_direction", "option"] == "degas":
            # step = int(-1*dp_step) # pressure step in bars
            if "final_P" in setup:
                final = int(setup.loc[run, "final_P"])
            else:
                final = 1.0
        elif models.loc["gassing_direction", "option"] == "regas":
            # step = int(dp_step)
            final = int(setup.loc[run, "final_P"])
    elif (
        models.loc["T_variation", "option"] == "polythermal"
    ):  # temperature ranges and options
        PT["P"] = setup.loc[run, "P_bar"]
        final = int(setup.loc[run, "final_T"])
        if setup.loc[run, "final_T"] > setup.loc[run, "T_C"]:
            initial = int(round(PT["T"]))
            # step = int(dp_step) # temperature step in 'C
        elif setup.loc[run, "final_T"] < setup.loc[run, "T_C"]:
            initial = int(round(PT["T"]))
            # step = int(-1.*dp_step) # temperature step in 'C

    # add some gas to the system if doing open-system regassing
    if (
        models.loc["gassing_direction", "option"] == "regas"
        and models.loc["gassing_style", "option"] == "open"
    ):
        gas_mf = {
            "O2": mg.xg_O2(PT, melt_wf, models),
            "CO": mg.xg_CO(PT, melt_wf, models),
            "CO2": mg.xg_CO2(PT, melt_wf, models),
            "H2": mg.xg_H2(PT, melt_wf, models),
            "H2O": mg.xg_H2O(PT, melt_wf, models),
            "CH4": mg.xg_CH4(PT, melt_wf, models),
            "S2": mg.xg_S2(PT, melt_wf, models),
            "SO2": mg.xg_SO2(PT, melt_wf, models),
            "H2S": mg.xg_H2S(PT, melt_wf, models),
            "OCS": mg.xg_OCS(PT, melt_wf, models),
            "X": mg.xg_X(PT, melt_wf, models),
            "Xg_t": mg.Xg_tot(PT, melt_wf, models),
            "wt_g": 0.0,
        }
        new_comp = c.new_bulk_regas_open(PT, melt_wf, bulk_wf, gas_mf, dwtg, models)
        bulk_wf = {
            "C": new_comp["wt_C"],
            "H": new_comp["wt_H"],
            "O": new_comp["wt_O"],
            "S": new_comp["wt_S"],
            "Fe": new_comp["wt_Fe"],
            "X": new_comp["wt_X"],
            "Wt": new_comp["Wt"],
        }

    # run over different pressures #
    number_of_step = 0.0
    if models.loc["gassing_direction", "option"] == "degas":
        max_number_of_step = initial
    elif models.loc["gassing_direction", "option"] == "regas":
        max_number_of_step = final - initial

    PT["P"] = initial
    last_successful_P = math.floor(PT["P"])

    with tqdm.tqdm(total=max_number_of_step) as tqdmsteps:
        while PT["P"] > 1.0:
            # for i in range(initial,final,step): # P is pressure in bars or T is
            # temperature in 'C
            number_of_step = number_of_step + 1.0
            eq_Fe = models.loc["eq_Fe", "option"]
            # guesses_original = guesses # store original guesses in case the
            # calculation needs to be restarted
            original_guessx, original_guessy, original_guessz, original_guessw = (
                guesses["guessx"],
                guesses["guessy"],
                guesses["guessz"],
                guesses["guessw"],
            )

            if dp_step_choice == "auto":
                if models.loc["gassing_style", "option"] == "open":
                    dp_step = 1.0
                else:
                    if PT["P"] > 5000.0:
                        dp_step = 500.0
                    elif PT["P"] > 200.0:
                        dp_step = 100.0
                    elif PT["P"] > 50.0:
                        dp_step = 10.0
                    else:
                        dp_step = 1.0

            if number_of_step == 1.0:
                if dp_step_choice == "user":
                    dp_step_user = dp_step
                dp_step = 0.0

            if models.loc["gassing_direction", "option"] == "regas":
                dp_step = -1.0 * dp_step

            if models.loc["P_variation", "option"] == "polybaric":
                # P = i - dp_step
                P = PT["P"] - dp_step
                if P < dp_step or P < 1.0:
                    P = 1.0
                PT["P"] = P
            elif models.loc["T_variation", "option"] == "polythermal":
                T = initial - dp_step
                PT["T"] = T

            if (
                models.loc["gassing_style", "option"] == "open"
            ):  # check melt is still vapor-saturated
                PT_ = {"P": PT["P"], "T": PT["T"]}
                if models.loc["COH_species", "option"] == "H2O-CO2 only":
                    P_sat_, P_sat_H2O_CO2_result = c.P_sat_H2O_CO2(
                        PT_, melt_wf, models, psat_tol, nr_step, nr_tol
                    )
                    conc = {
                        "wm_H2O": P_sat_H2O_CO2_result["wm_H2O"],
                        "wm_CO2": P_sat_H2O_CO2_result["wm_CO2"],
                        "wm_H2": 0.0,
                        "wm_CO": 0.0,
                        "wm_CH4": 0.0,
                        "wm_H2S": 0.0,
                        "wm_S2m": 0.0,
                        "wm_S6p": 0.0,
                        "ST": 0.0,
                    }
                    frac = c.melt_species_ratios(conc)
                else:
                    P_sat_, conc, frac = c.P_sat(
                        PT_, melt_wf, models, psat_tol, nr_step, nr_tol
                    )
                if models.loc["gassing_direction", "option"] == "degas":
                    checkingP = PT["P"]
                    while P_sat_ < checkingP:
                        checkingP = checkingP - dp_step
                        PT_["P"] = checkingP
                        if models.loc["COH_species", "option"] == "H2O-CO2 only":
                            P_sat_, P_sat_H2O_CO2_result = c.P_sat_H2O_CO2(
                                PT_, melt_wf, models, psat_tol, nr_step, nr_tol
                            )
                            conc = {
                                "wm_H2O": P_sat_H2O_CO2_result["wm_H2O"],
                                "wm_CO2": P_sat_H2O_CO2_result["wm_CO2"],
                                "wm_H2": 0.0,
                                "wm_CO": 0.0,
                                "wm_CH4": 0.0,
                                "wm_H2S": 0.0,
                                "wm_S2m": 0.0,
                                "wm_S6p": 0.0,
                                "ST": 0.0,
                            }
                            frac = c.melt_species_ratios(conc)
                        else:
                            P_sat_, conc, frac = c.P_sat(
                                PT_, melt_wf, models, psat_tol, nr_step, nr_tol
                            )
                    PT["P"] = checkingP

            if P_sat_ > PT["P"] or models.loc["gassing_direction", "option"] == "regas":
                # work out equilibrium partitioning between melt and gas phase
                with warnings.catch_warnings():
                    warnings.simplefilter(
                        "ignore" if suppress_warnings else "default",
                        category=RuntimeWarning,
                    )
                    (
                        xg,
                        conc,
                        melt_and_gas,
                        guesses,
                        new_models,
                        solve_species,
                        mass_balance,
                    ) = eq.mg_equilibrium(
                        PT, melt_wf, bulk_wf, models, nr_step_eq, nr_tol, guesses
                    )
                models = new_models
                # if xg["xg_O2"] == 1.0:
                #    print('tried resetting guesses')
                #    guesses = eq.initial_guesses(run,PT,melt_wf,setup,models,system)
                #    xg, conc, melt_and_gas, guesses, new_models, solve_species,
                #    mass_balance = eq.mg_equilibrium(PT,melt_wf,bulk_wf,models,
                #    nr_step_eq, nr_tol,guesses)
                #    models = new_models
                if models.loc["gassing_style", "option"] == "closed":
                    # if xg["xg_O2"] == 1.0:
                    #    current_melt = {'SiO2': melt_wf["SiO2"], 'TiO2': melt_wf
                    #    ["TiO2"],
                    #    'Al2O3': melt_wf["Al2O3"], 'FeOT': melt_wf["FeOT"], 'Fe2O3T':
                    #    melt_wf["Fe2O3T"], 'FeO': melt_wf["FeO"], 'Fe2O3':
                    #    melt_wf["Fe2O3"], 'MgO': melt_wf["MgO"], 'MnO': melt_wf["MnO"],
                    #    'CaO': melt_wf["CaO"], 'Na2O': melt_wf["Na2O"], 'K2O':
                    #    melt_wf["K2O"], 'P2O5': melt_wf["P2O5"], 'logfO2_i':
                    #    melt_wf["logfO2_i"], 'Fe3FeT_i': melt_wf["Fe3FeT_i"], 'DNNO':
                    #    melt_wf["DNNO"], 'DFMQ': melt_wf["DFMQ"], 'S6ST_i':
                    #    melt_wf["S6ST_i"], "ST":melt_wf["ST"],"CO2":melt_wf["CO2"],
                    #    "H2OT":melt_wf["H2OT"],"HT":melt_wf["HT"],"CT":melt_wf["CT"],
                    #    "XT":melt_wf["XT"]}
                    #    P_sat_, conc, frac = c.P_sat(PT,current_melt,models,psat_tol,
                    #    nr_step,nr_tol)
                    if xg["xg_O2"] == 1.0:
                        guesses = {
                            "guessx": original_guessx,
                            "guessy": original_guessy,
                            "guessz": original_guessz,
                            "guessw": original_guessw,
                        }
                        if dp_step < 1.0 or dp_step == 1.0:
                            if PT["P"] <= 10.0:
                                print("P < 10 bar, trying P = 1 bar")
                                PT["P"] = 1.0
                                with warnings.catch_warnings():
                                    warnings.simplefilter(
                                        "ignore" if suppress_warnings else "default",
                                        category=RuntimeWarning,
                                    )
                                    (
                                        xg,
                                        conc,
                                        melt_and_gas,
                                        guesses,
                                        new_models,
                                        solve_species,
                                        mass_balance,
                                    ) = eq.mg_equilibrium(
                                        PT,
                                        melt_wf,
                                        bulk_wf,
                                        models,
                                        nr_step_eq,
                                        nr_tol,
                                        guesses,
                                    )
                                models = new_models
                                if xg["xg_O2"] == 1.0:
                                    results.columns = results.iloc[0]
                                    results = results[1:]
                                    results.reset_index(drop=True, inplace=True)
                                    if models.loc["output csv", "option"] == "True":
                                        results.to_csv(
                                            "results_gassing_chemistry.csv",
                                            index=False,
                                            header=True,
                                        )
                                    print(
                                        "solver failed, calculation aborted at P = ",
                                        last_successful_P,
                                        datetime.datetime.now(),
                                    )
                                    return results
                            print(
                                "solver failed at P = ",
                                PT["P"],
                                "with dp_step = ",
                                dp_step,
                                ", increasing step size by factor 10",
                            )
                            dp_step = dp_step * 10.0
                        else:
                            print(
                                "solver failed at P = ",
                                PT["P"],
                                "with dp_step = ",
                                dp_step,
                                ", decreasing step size by factor 10",
                            )
                            dp_step = dp_step / 10.0
                        newP = last_successful_P - dp_step
                        if newP < 1.0:
                            newP = 1.0
                        PT["P"] = newP
                        guesses = {
                            "guessx": original_guessx,
                            "guessy": original_guessy,
                            "guessz": original_guessz,
                            "guessw": original_guessw,
                        }
                        with warnings.catch_warnings():
                            warnings.simplefilter(
                                "ignore" if suppress_warnings else "default",
                                category=RuntimeWarning,
                            )
                            (
                                xg,
                                conc,
                                melt_and_gas,
                                guesses,
                                new_models,
                                solve_species,
                                mass_balance,
                            ) = eq.mg_equilibrium(
                                PT,
                                melt_wf,
                                bulk_wf,
                                models,
                                nr_step_eq,
                                nr_tol,
                                guesses,
                            )
                        models = new_models
                if xg["xg_O2"] == 1.0:
                    if dp_step > 1.0:
                        print(
                            "solver failed at P = ",
                            PT["P"],
                            "with dp_step = ",
                            dp_step,
                            ", decreasing step size to 1 bar",
                        )
                        dp_step = 1.0
                        newP = last_successful_P - dp_step
                        PT["P"] = newP
                        guesses = {
                            "guessx": original_guessx,
                            "guessy": original_guessy,
                            "guessz": original_guessz,
                            "guessw": original_guessw,
                        }
                        with warnings.catch_warnings():
                            warnings.simplefilter(
                                "ignore" if suppress_warnings else "default",
                                category=RuntimeWarning,
                            )
                            (
                                xg,
                                conc,
                                melt_and_gas,
                                guesses,
                                new_models,
                                solve_species,
                                mass_balance,
                            ) = eq.mg_equilibrium(
                                PT,
                                melt_wf,
                                bulk_wf,
                                models,
                                nr_step_eq,
                                nr_tol,
                                guesses,
                            )
                        models = new_models
                if xg["xg_O2"] == 1.0:
                    results.columns = results.iloc[0]
                    results = results[1:]
                    results.reset_index(drop=True, inplace=True)
                    if models.loc["output csv", "option"] == "True":
                        results.to_csv(
                            "results_gassing_chemistry.csv", index=False, header=True
                        )
                    print(
                        "solver failed, calculation aborted at P = ",
                        last_successful_P,
                        datetime.datetime.now(),
                    )
                    return results
                # gas composition
                gas_mf = {
                    "O2": xg["xg_O2"],
                    "CO": xg["xg_CO"],
                    "S2": xg["xg_S2"],
                    "CO2": xg["xg_CO2"],
                    "H2O": xg["xg_H2O"],
                    "H2": xg["xg_H2"],
                    "CH4": xg["xg_CH4"],
                    "SO2": xg["xg_SO2"],
                    "H2S": xg["xg_H2S"],
                    "OCS": xg["xg_OCS"],
                    "X": xg["xg_X"],
                    "Xg_t": xg["Xg_t"],
                    "wt_g": melt_and_gas["wt_g"],
                }
            # else: # NEEDS SORTING ###
            # conc = eq.melt_speciation(PT,melt_wf,models,nr_step,nr_tol)
            # frac = c.melt_species_ratios(conc)
            # wm_ST_ = wm_S_ + wm_S6p_
            # S62 = S6T/S2m_ST
            # Fe3T = melt_wf["Fe3FeT"]
            # Fe32 = mg.overtotal2ratio(Fe3T)
            # xg = {"xg_O2":0., "xg_H2":0., "xg_S2":0., "xg_H2O":0., "xg_CO":0.,
            #      "xg_CO2":0., "xg_SO2":0., "xg_CH4":0., "xg_H2S":0., "xg_OCS":0.,
            #      "xg_X":0., "Xg_t":0.}
            # if number_of_step == 1:
            #    melt_and_gas = {}
            # melt_and_gas["wt_g_O"],melt_and_gas["wt_g_C"],melt_and_gas["wt_g_H"],
            # melt_and_gas["wt_g_S"],melt_and_gas["wt_g_X"],melt_and_gas["wt_g"] =
            # 0.,0.,0.,0.,0.
            # guesses = eq.initial_guesses(run,PT,melt_wf,setup,models,system)
            # solve_species = "na"
            # gas_mf = {"O2":xg["xg_O2"],"CO":xg["xg_CO"],"S2":xg["xg_S2"],
            #          "CO2":xg["xg_CO2"],"H2O":xg["xg_H2O"],"H2":xg["xg_H2"],
            #          "CH4":xg["xg_CH4"],"SO2":xg["xg_SO2"],"H2S":xg["xg_H2S"],
            #          "OCS":xg["xg_OCS"],"X":xg["xg_X"],"Xg_t":xg["Xg_t"],
            #          "wt_g":melt_and_gas["wt_g"]}

            if P_sat_ > PT["P"] or models.loc["gassing_direction", "option"] == "regas":
                if (
                    models.loc["gassing_style", "option"] == "open"
                    and models.loc["gassing_direction", "option"] == "degas"
                ):
                    if number_of_step == 1:
                        gas_mf_all = gas_mf
                    else:
                        gas_mf_all = c.gas_comp_all_open(gas_mf, gas_mf_all, models)
                if models.loc["COH_species", "option"] == "H2O-CO2 only":
                    Fe3T = melt_wf["Fe3FeT"]

            # set melt composition for forward calculation
            melt_wf["CO2"] = conc["wm_CO2"]
            melt_wf["H2OT"] = conc["wm_H2O"]
            melt_wf["H2"] = conc["wm_H2"]
            melt_wf["CO"] = conc["wm_CO"]
            melt_wf["CH4"] = conc["wm_CH4"]
            melt_wf["H2S"] = conc["wm_H2S"]
            melt_wf["S6+"] = (
                conc["wm_SO3"] / mdv.species.loc["SO3", "M"]
            ) * mdv.species.loc["S", "M"]
            melt_wf["S2-"] = conc["wm_S2m"]
            melt_wf["ST"] = conc["wm_ST"]
            melt_wf["XT"] = conc["wm_X"]
            melt_wf["Fe3FeT"] = conc["Fe3T"]
            if P_sat_ < PT["P"]:
                bulk_comp = c.bulk_composition(run, PT, melt_wf, setup, models)

            # check for sulfur saturation and display warning in outputs
            sulf_sat_result = c.sulfur_saturation(PT, melt_wf, models)
            if sulf_sat_result["sulfide_sat"] == "yes":
                warning = "WARNING: sulfide-saturated"
            elif sulf_sat_result["sulfate_sat"] == "yes":
                warning = "WARNING: sulfate-saturated"
            else:
                warning = ""

            # calculate fO2
            if eq_Fe == "yes":
                fO2_ = mdv.f_O2(PT, melt_wf, models)
            elif eq_Fe == "no":
                fO2_ = gas_mf["O2"] * mdv.y_O2(PT, models) * PT["P"]

            wm_CO2eq, wm_H2Oeq = mg.melt_H2O_CO2_eq(melt_wf)
            melt_comp = mg.melt_normalise_wf(melt_wf, "yes", "no")
            frac = c.melt_species_ratios(conc)

            # store results
            results_headers_table_sample_name, results_values_table_sample_name = (
                results_table_sample_name(setup, run)
            )
            results_headers_table_melt_comp_etc, results_values_table_melt_comp_etc = (
                results_table_melt_comp_etc(PT, melt_comp, conc, frac, melt_wf)
            )
            results_headers_table_model_options, results_values_table_model_options = (
                results_table_model_options(models)
            )
            (
                results_headers_table_f_p_xg_y_M_C_K_d,
                results_values_table_f_p_xg_y_M_C_K_d,
            ) = results_table_f_p_xg_y_M_C_K_d(PT, melt_wf, models)
            results_headers_table_sat, results_values_table_sat = results_table_sat(
                sulf_sat_result, PT, melt_wf, models
            )
            results_values_table_melt_vol = pd.DataFrame(
                [
                    [
                        wm_H2Oeq * 100.0,
                        wm_CO2eq * 1000000.0,
                        conc["wm_ST"] * 1000000.0,
                        melt_wf["XT"] * 1000000.0,
                    ]
                ]
            )
            results_values_table_wtg_etc = pd.DataFrame(
                [
                    [
                        melt_and_gas["wt_g"] * 100.0,
                        melt_and_gas["wt_g_O"],
                        melt_and_gas["wt_g_C"],
                        melt_and_gas["wt_g_H"],
                        melt_and_gas["wt_g_S"],
                        melt_and_gas["wt_g_X"],
                        melt_and_gas["wt_O"] * 100.0,
                        melt_and_gas["wt_C"] * 100.0,
                        melt_and_gas["wt_H"] * 100.0,
                        melt_and_gas["wt_S"] * 100.0,
                        melt_and_gas["wt_X"] * 100.0,
                        solve_species,
                        mass_balance["C"],
                        mass_balance["O"],
                        mass_balance["H"],
                        mass_balance["S"],
                    ]
                ]
            )
            if (
                models.loc["gassing_style", "option"] == "open"
                and models.loc["gassing_direction", "option"] == "degas"
            ):
                results_values_table_open_all_gas = pd.DataFrame(
                    [
                        [
                            gas_mf_all["O2"],
                            gas_mf_all["H2"],
                            gas_mf_all["H2O"],
                            gas_mf_all["S2"],
                            gas_mf_all["SO2"],
                            gas_mf_all["H2S"],
                            gas_mf_all["CO2"],
                            gas_mf_all["CO"],
                            gas_mf_all["CH4"],
                            gas_mf_all["OCS"],
                            gas_mf_all["X"],
                            mg.gas_CS_alt(gas_mf_all),
                        ]
                    ]
                )
                results1 = pd.concat(
                    [
                        results_values_table_sample_name,
                        results_values_table_melt_comp_etc,
                        results_values_table_melt_vol,
                        results_values_table_sat,
                        results_values_table_f_p_xg_y_M_C_K_d,
                        results_values_table_wtg_etc,
                        results_values_table_open_all_gas,
                        results_values_table_model_options,
                    ],
                    axis=1,
                )
            else:
                results1 = pd.concat(
                    [
                        results_values_table_sample_name,
                        results_values_table_melt_comp_etc,
                        results_values_table_melt_vol,
                        results_values_table_sat,
                        results_values_table_f_p_xg_y_M_C_K_d,
                        results_values_table_wtg_etc,
                        results_values_table_model_options,
                    ],
                    axis=1,
                )
            results = pd.concat([results, results1])

            # equilibrium isotope fractionation
            if models.loc["isotopes", "option"] == "yes":
                raise TypeError("This is not currently supported")
                if models.loc["H2S", "option"] == "yes":
                    print("not currently possible")
                # A, B = iso.i2s6("S", PT, R_i, melt_wf, gas_mf, i_nr_step, i_nr_tol,
                # guessx)
                # RS_Sm, RS_H2S, RS_SO4, RS_S2, RS_SO2, RS_OCS = A
                # RS_m, RS_g = B
                a_H2S_S_, a_SO4_S_, a_S2_S_, a_SO2_S_, a_OCS_S_ = iso.i2s6_S_alphas(PT)
                # xg_SO3_ = 0.0
                results2 = pd.DataFrame(
                    [
                        [
                            PT["P"],
                            PT["T"],
                            # xg_O2_,
                            # xg_CO_,
                            # xg_CO2_,
                            # xg_H2_,
                            # xg_H2O_,
                            # xg_CH4_,
                            # xg_S2_,
                            # xg_SO2_,
                            # xg_SO3_,
                            # xg_H2S_,
                            # xg_OCS_,
                            # wt_g,
                            # wm_CO2_,
                            # wm_H2O_,
                            # wm_H2_,
                            # wm_S_,
                            # wm_SO3_,
                            # wm_ST_,
                            Fe3T,
                            # S6T,
                            mg.fO22Dbuffer(PT, fO2_, "FMQ"),
                            mg.fO22Dbuffer(PT, fO2_, "NNO"),
                            # SCSS_,
                            # sulfide_sat,
                            # SCAS_,
                            # sulfate_sat,
                            # RS_Sm,
                            # RS_SO4,
                            # RS_H2S,
                            # RS_SO2,
                            # RS_S2,
                            # RS_OCS,
                            # RS_m,
                            # RS_g,
                            # ratio2delta("VCDT", RS_Sm),
                            # ratio2delta("VCDT", RS_SO4),
                            # ratio2delta("VCDT", RS_H2S),
                            # ratio2delta("VCDT", RS_SO2),
                            # ratio2delta("VCDT", RS_S2),
                            # ratio2delta("VCDT", RS_OCS),
                            # ratio2delta("VCDT", RS_m),
                            # ratio2delta("VCDT", RS_g),
                            a_H2S_S_,
                            a_SO4_S_,
                            a_S2_S_,
                            a_SO2_S_,
                            a_OCS_S_,
                            # RS_g / RS_m,
                        ]
                    ]
                )
                results_isotopes = pd.concat(
                    [results_isotopes, results2], ignore_index=True
                )
                if models.loc["output csv", "option"] == "True":
                    results_isotopes.to_csv(
                        "results_gassing_isotopes.csv", index=False, header=False
                    )

            if models.loc["print status", "option"] == "True":
                if number_of_step % 100 == 0:
                    print(
                        PT["T"],
                        PT["P"],
                        mg.fO22Dbuffer(PT, fO2_, "FMQ", models),
                        warning,
                        datetime.datetime.now(),
                    )

            # recalculate bulk composition if needed
            if models.loc["gassing_style", "option"] == "open":
                results_me = mg.melt_elements(melt_wf, bulk_wf, gas_mf)
                if models.loc["gassing_direction", "option"] == "degas":
                    Wt_ = bulk_wf["Wt"]
                    if results_me["wm_C"] < 1.0e-7:  # 0.1 ppm C
                        results_me["wm_C"] = 0.0
                    if results_me["wm_H"] < 1.0e-7:  # 0.1 ppm H
                        results_me["wm_H"] = 0.0
                    if results_me["wm_S"] < 1.0e-7:  # 0.1 ppm S
                        results_me["wm_S"] = 0.0
                    if results_me["wm_X"] < 1.0e-7:  # 0.1 ppm X
                        results_me["wm_X"] = 0.0
                    bulk_wf = {
                        "C": results_me["wm_C"],
                        "H": results_me["wm_H"],
                        "O": results_me["wm_O"],
                        "S": results_me["wm_S"],
                        "X": results_me["wm_X"],
                        "Fe": results_me["wm_Fe"],
                        "Wt": (Wt_ * (1.0 - melt_and_gas["wt_g"])),
                    }
                    melt_wf["CT"] = results_me["wm_C"]
                    melt_wf["HT"] = results_me["wm_H"]
                    melt_wf["ST"] = results_me["wm_S"]
                    melt_wf["XT"] = results_me["wm_X"]
                    system = eq.set_system(melt_wf, models)
                elif models.loc["gassing_direction", "option"] == "regas":
                    results_nbro = c.new_bulk_regas_open(
                        PT, melt_wf, bulk_wf, gas_mf, dwtg, models
                    )
                    bulk_wf = {
                        "C": results_nbro["wt_C"],
                        "H": results_nbro["wt_H"],
                        "O": results_nbro["wt_O"],
                        "S": results_nbro["wt_S"],
                        "X": results_nbro["wt_X"],
                        "Fe": results_nbro["wt_Fe"],
                        "Wt": results_nbro["Wt"],
                    }
                    # melt_wf["CT"] = results_nbro["wm_C"]
                    # melt_wf["HT"] = results_nbro["wm_H"]
                    # melt_wf["ST"] = results_nbro["wm_S"]
                    # melt_wf["XT"] = results_nbro["wm_X"]
            if models.loc["crystallisation", "option"] == "yes":
                wt_C_ = bulk_wf["C"]
                wt_H_ = bulk_wf["H"]
                wt_O_ = bulk_wf["O"]
                wt_S_ = bulk_wf["S"]
                wt_X_ = bulk_wf["X"]
                wt_Fe_ = bulk_wf["Fe"]
                wt_ = bulk_wf["Wt"]
                Xst = setup.loc[run, "crystallisation_pc"] / 100.0
                bulk_wf = {
                    "C": wt_C_ * (1.0 / (1.0 - Xst)),
                    "H": wt_H_ * (1.0 / (1.0 - Xst)),
                    "O": wt_O_ * (1.0 / (1.0 - Xst)),
                    "S": wt_S_ * (1.0 / (1.0 - Xst)),
                    "X": wt_X_ * (1.0 / (1.0 - Xst)),
                    "Fe": wt_Fe_ * (1.0 / (1.0 - Xst)),
                    "Wt": wt_ * (1.0 - Xst),
                }

            tqdmsteps.update(abs(dp_step))

            if models.loc["gassing_direction", "option"] == "regas":
                if (PT["P"] + dp_step) >= final:
                    break

            if number_of_step == 1.0:
                if dp_step_choice == "user":
                    dp_step = dp_step_user

            last_successful_P = PT["P"]

    results.columns = results.iloc[0]
    results = results[1:]
    results.reset_index(drop=True, inplace=True)
    if models.loc["output csv", "option"] == "True":
        results.to_csv("results_gassing_chemistry.csv", index=False, header=True)

    if models.loc["print status", "option"] == "True":
        print("done", datetime.datetime.now())

    return results


#########################
# calculate isobars #####
#########################
def calc_isobar(
    setup,
    run=0,
    models=mdv.default_models,
    initial_P=1000.0,
    final_P=10000.0,
    step_P=1000.0,
):
    """Calculates H2O-CO2-only isobars for given T, melt composition, initial/final P,
    and P step-size.

    Args:
        setup (pandas.DataFrame): Melt composition to be used, requires following headers (notes in [] are not part of the headers): Sample; T_C; DNNO or DFMQ or logfO2 or (Fe2O3 and FeO) or Fe3FeT or S6ST; SiO2, TiO2, Al2O3, (Fe2O3T or FeOT unless Fe2O3 and FeO given), MnO, MgO, CaO, Na2O, K2O, P2O5[concentrations are in wt%].
        run (int, optional): Integer of the row in the setup file to run (note the first row under the headers is row 0). Defaults to 0.
        models (_type_, optional): Model options. Defaults to mdv.default_models.
        initial_P (float, optional): Starting pressure in bar for isobar calculation. Defaults to 1000.0.
        final_P (float, optional): Final pressure in bar for isobar calculation. Defaults to 10000.0.
        step_P (float, optional): Pressure step in bar for calculating isobars between starting and final pressures. Defaults to 1000.0.

    Returns:
        pandas.DataFrame: Results from isobar calculation


    Outputs
    -------
    If output csv = yes in models, results_gassing_chemistry: csv file
    """
    if models.loc["COH_species", "option"] == "H2O-CO2 only":
        PT = {"T": setup.loc[run, "T_C"]}

        # check if any options need to be read from the setup file rather than the
        # models file
        models = options_from_setup(run, models, setup)

        # set up results table
        results = pd.DataFrame([["P_bar", "H2O_wtpc", "CO2_ppm"]])

        initial_P = int(initial_P)
        final_P = int(final_P + 1)
        step_P = int(step_P)
        melt_wf = mg.melt_comp(run, setup)

        for n in range(initial_P, final_P, step_P):
            PT["P"] = n  # pressure in bars
            results1 = c.calc_isobar_CO2H2O(PT, melt_wf, models)
            results = pd.concat([results, results1], ignore_index=True)
            if models.loc["print status", "option"] == "True":
                print(setup.loc[run, "Sample"], n)
        results.columns = results.iloc[0]
        results = results[1:]

    else:
        raise TypeError("COH_species option must be H2O-CO2 only")
    if models.loc["output csv", "option"] == "True":
        results.to_csv("results_isobars.csv", index=False, header=False)

    return results


#################################
# calculate pure solubility #####
#################################
def calc_pure_solubility(setup, run=0, models=mdv.default_models, initial_P=5000.0):
    """
    Calculates the solubility of pure H2O and pure CO2.

    Args:
        setup (pandas.DataFrame): Melt compositions to be used, requires following headers: Sample; T_C; SiO2, TiO2, Al2O3, (Fe2O3T or FeOT unless Fe2O3 and FeO given), MnO, MgO, CaO, Na2O, K2O, P2O5, H2O; Note: concentrations (unless otherwise stated) are in wt%.
        run (int, optional): Row number of input data
        models (pandas.DataFrame): Model options
        initial_P (float, optional): Highest pressure in bar for solubility calculation. Default = 5000.0

    Returns:
        pandas.DataFrame: Results of pure solubility calculation.


    Outputs
    -------
    results_pure_solubility.csv: csv file (if output csv = yes in models)

    """
    if models.loc["print status", "option"] == "True":
        print(setup.loc[run, "Sample"], initial_P)
    PT = {"T": setup.loc[run, "T_C"]}

    # check if any options need to be read from the setup file rather than the models
    # file
    models = options_from_setup(run, models, setup)

    # set up results table
    results = pd.DataFrame([["P_bar", "H2O_wtpc", "CO2_ppmw"]])

    initial_P = int(initial_P)

    for n in range(initial_P, 1, -1):
        PT["P"] = n  # pressure in bars
        melt_wf = mg.melt_comp(run, setup)
        results1 = c.calc_pure_solubility(PT, melt_wf, models)
        results = pd.concat([results, results1], ignore_index=True)

    results.columns = results.iloc[0]
    results = results[1:]
    if models.loc["output csv", "option"] == "True":
        results.to_csv("results_pure_solubility.csv", index=False, header=False)
    if models.loc["print status", "option"] == "True":
        print("done")

    return results


######################################
# calculate solubility constants #####
######################################
# print capacities for multiple melt compositions in input file
def calc_sol_consts(setup, first_row=0, last_row=None, models=mdv.default_models):
    """Calculate solubility functions for given melt composition and conditions.

    Args:
        setup (pandas.DataFrame): Input data
        first_row (int, optional): First row of input data to run calculation for. Defaults to 0.
        last_row (int, optional): Last row of input data to run calculation for. Defaults to None.
        models (pandas.DataFrame, optional): Model options. Defaults to mdv.default_models.

    Returns:
        pandas.DataFrame: Values of solubility functions

    Outputs:
        'capacities.csv' is 'output_csv' is True
    """
    # set up results table
    results_headers_models = pd.DataFrame(
        [
            [
                "species X opt",
                "Hspeciation opt",
                "fO2 opt",
                "NNObuffer opt",
                "FMQbuffer opt",
                "carbon dioxide opt",
                "water opt",
                "hydrogen opt",
                "sulfide opt",
                "sulfate opt",
                "hydrogen sulfide opt",
                "methane opt",
                "carbon monoxide opt",
                "species X solubility opt",
                "Cspeccomp opt",
                "Hspeccomp opt",
                "Date",
            ]
        ]
    )
    results_headers_values = pd.DataFrame(
        [
            [
                "Sample",
                "Pressure (bar)",
                "T ('C)",
                "SiO2",
                "TiO2",
                "Al2O3",
                "FeOT",
                "MnO",
                "MgO",
                "CaO",
                "Na2O",
                "K2O",
                "P2O5",
                "H2O",
                "CO2 (ppm)",
                "ST (ppm)",
                "Fe3+/FeT",
                "fO2 DFMQ",
                "ln[C_CO2T]",
                "ln[C_H2OT]",
                "ln[C_S2-]",
                "ln[C_S6+]",
                "ln[C_H2S]",
                "ln[C_H2]",
                "ln[C_CO]",
                "ln[C_CH4]",
                "ln[C_X]",
                "M_m_SO",
            ]
        ]
    )
    results_headers = pd.concat(
        [results_headers_values, results_headers_models], axis=1
    )

    if last_row is None:
        last_row = len(setup)

    for n in range(
        first_row, last_row, 1
    ):  # n is number of rows of data in conditions file
        run = n

        # check if any options need to be read from the setup file rather than the
        # models file
        models = options_from_setup(run, models, setup)

        PT = {"T": setup.loc[run, "T_C"]}
        melt_wf = mg.melt_comp(run, setup)
        PT["P"] = setup.loc[run, "P_bar"]
        melt_wf["Fe3FeT"] = mg.Fe3FeT_i(PT, melt_wf, models)
        C_CO32 = mdv.C_CO3(PT, melt_wf, models)
        C_H2OT = mdv.C_H2O(PT, melt_wf, models)
        C_S2 = mdv.C_S(PT, melt_wf, models)
        C_S6 = mdv.C_SO4(PT, melt_wf, models)
        C_H2S = mdv.C_H2S(PT, melt_wf, models)
        C_H2 = mdv.C_H2(PT, melt_wf, models)
        C_CO = mdv.C_CO(PT, melt_wf, models)
        C_CH4 = mdv.C_CH4(PT, melt_wf, models)
        C_X = mdv.C_X(PT, melt_wf, models)
        fO2_ = mg.fO22Dbuffer(PT, mdv.f_O2(PT, melt_wf, models), "FMQ", models)
        M_m = mg.M_m_SO(melt_wf)
        melt_comp = mg.melt_normalise_wf(melt_wf, "yes", "no")

        # store results
        results_values_models = pd.DataFrame(
            [
                [
                    models.loc["species X", "option"],
                    models.loc["Hspeciation", "option"],
                    models.loc["fO2", "option"],
                    models.loc["NNObuffer", "option"],
                    models.loc["FMQbuffer", "option"],
                    models.loc["carbon dioxide", "option"],
                    models.loc["water", "option"],
                    models.loc["hydrogen", "option"],
                    models.loc["sulfide", "option"],
                    models.loc["sulfate", "option"],
                    models.loc["hydrogen sulfide", "option"],
                    models.loc["methane", "option"],
                    models.loc["carbon monoxide", "option"],
                    models.loc["species X solubility", "option"],
                    models.loc["Cspeccomp", "option"],
                    models.loc["Hspeccomp", "option"],
                    datetime.datetime.now(),
                ]
            ]
        )
        results_values_values = pd.DataFrame(
            [
                [
                    setup.loc[run, "Sample"],
                    PT["P"],
                    PT["T"],
                    melt_comp["SiO2"] * 100.0,
                    melt_comp["TiO2"] * 100.0,
                    melt_comp["Al2O3"] * 100.0,
                    melt_comp["FeOT"] * 100.0,
                    melt_comp["MnO"] * 100.0,
                    melt_comp["MgO"] * 100.0,
                    melt_comp["CaO"] * 100.0,
                    melt_comp["Na2O"] * 100.0,
                    melt_comp["K2O"] * 100.0,
                    melt_comp["P2O5"] * 100.0,
                    setup.loc[run, "H2O"],
                    setup.loc[run, "CO2ppm"],
                    setup.loc[run, "STppm"],
                    melt_wf["Fe3FeT"],
                    fO2_,
                    math.log(C_CO32),
                    math.log(C_H2OT),
                    math.log(C_S2),
                    math.log(C_S6),
                    math.log(C_H2S),
                    math.log(C_H2),
                    math.log(C_CO),
                    math.log(C_CH4),
                    math.log(C_X),
                    M_m,
                ]
            ]
        )
        results1 = pd.concat([results_values_values, results_values_models], axis=1)

        if n == first_row:
            results = pd.concat([results_headers, results1])
        else:
            results = pd.concat([results, results1])

        if models.loc["print status", "option"] == "True":
            print(
                n,
                setup.loc[run, "Sample"],
                math.log(C_CO32),
                math.log(C_H2OT),
                math.log(C_S2),
                math.log(C_S6),
                math.log(C_H2S),
                math.log(C_H2),
                math.log(C_CO),
                math.log(C_CH4),
                M_m,
            )

    results.columns = results.iloc[0]
    results = results[1:]

    if models.loc["output csv", "option"] == "True":
        results.to_csv("capacities.csv", index=False, header=False)

    return results


#######################################
# calculate fugacity coefficients #####
#######################################
def calc_fugacity_coefficients(
    setup, first_row=0, last_row=None, models=mdv.default_models
):
    """Calculates values of fugacity coefficients for given conditions.

    Args:
        setup (pandas.DataFrame): Input data
        first_row (int, optional): First row of input data to run calculation for. Defaults to 0.
        last_row (int, optional): Last row of input data to run calculation for. Defaults to None.
        models (pandas.DataFrame, optional): Model options. Defaults to mdv.default_models.

    Returns:
        pandas.DataFrame: Values of fugacity coefficients

    Outputs:
        'results_fugacity_coefficients.csv' is 'output_csv' is True
    """
    # set up results table
    results_headers_models = pd.DataFrame(
        [
            [
                "y_CO2 opt",
                "y_SO2 opt",
                "y_H2S opt",
                "y_H2 opt",
                "y_O2 opt",
                "y_S2 opt",
                "y_CO opt",
                "y_CH4 opt",
                "y_H2O opt",
                "y_OCS opt",
                "y_X opt",
                "Date",
            ]
        ]
    )
    results_headers_values = pd.DataFrame(
        [
            [
                "Sample",
                "P_bar",
                "T_C",
                "yO2",
                "yH2",
                "yH2O",
                "yS2",
                "ySO2",
                "yH2S",
                "yCO2",
                "yCO",
                "yCH4",
                "yOCS",
                "yX",
            ]
        ]
    )
    results_headers = pd.concat(
        [results_headers_values, results_headers_models], axis=1
    )

    if last_row is None:
        last_row = len(setup)

    for n in range(
        first_row, last_row, 1
    ):  # n is number of rows of data in conditions file
        run = n

        # check if any options need to be read from the setup file rather than the
        # models file
        models = options_from_setup(run, models, setup)

        PT = {"T": setup.loc[run, "T_C"]}
        PT["P"] = setup.loc[run, "P_bar"]

        # store results
        results_values_models = pd.DataFrame(
            [
                [
                    models.loc["y_CO2", "option"],
                    models.loc["y_SO2", "option"],
                    models.loc["y_H2S", "option"],
                    models.loc["y_H2", "option"],
                    models.loc["y_O2", "option"],
                    models.loc["y_S2", "option"],
                    models.loc["y_CO", "option"],
                    models.loc["y_CH4", "option"],
                    models.loc["y_H2O", "option"],
                    models.loc["y_OCS", "option"],
                    models.loc["y_X", "option"],
                    datetime.datetime.now(),
                ]
            ]
        )
        results_values_values = pd.DataFrame(
            [
                [
                    setup.loc[run, "Sample"],
                    PT["P"],
                    PT["T"],
                    mdv.y_O2(PT, models),
                    mdv.y_H2(PT, models),
                    mdv.y_H2O(PT, models),
                    mdv.y_S2(PT, models),
                    mdv.y_SO2(PT, models),
                    mdv.y_H2S(PT, models),
                    mdv.y_CO2(PT, models),
                    mdv.y_CO(PT, models),
                    mdv.y_CH4(PT, models),
                    mdv.y_OCS(PT, models),
                    mdv.y_X(PT, models),
                ]
            ]
        )
        results1 = pd.concat([results_values_values, results_values_models], axis=1)

        if n == first_row:
            results = pd.concat([results_headers, results1])
        else:
            results = pd.concat([results, results1])

        if models.loc["print status", "option"] == "True":
            print(n, setup.loc[run, "Sample"], PT["P"])

    results.columns = results.iloc[0]
    results = results[1:]

    if models.loc["output csv", "option"] == "True":
        results.to_csv("results_fugacity_coefficients.csv", index=False, header=True)

    return results


###############################
# Use melt S oxybarometer #####
###############################
def calc_melt_S_oxybarometer(
    setup,
    first_row=0,
    last_row=None,
    models=mdv.default_models,
    p_tol=0.1,
    nr_step=1.0,
    nr_tol=1.0e-9,
):
    """
    Calculates the range in oxygen fugacity based on the melt sulfur content for
    multiple melt compositions given volatile-free melt composition, volatile content,
    temperature, and either pressure or assumes Pvsat.


    Args:
        setup (pandas.DataFrame): Melt compositions to be used, requires following headers: Sample, T_C, SiO2, TiO2, Al2O3, (Fe2O3T or FeOT unless Fe2O3 and FeO given), MnO, MgO, CaO, Na2O, K2O, P2O5, H2O and/or CO2ppm and/or STppm and/or Xppm. Note: concentrations (unless otherwise stated) are in wt%. Optional: P_bar is pressure is given (otherwise calculation is at Pvsat). Fe3FeT if P_bar is specified.
        models (pandas.DataFrame, optional): Model options
        first_row (int, optional): First row in the setup file to run (note the first row under the headers is row 0). Default = 0
        last_row: (int, optional): Last row in the setup file to run (note the first row under the headers is row 0). Default = None
        p_tol (float, optional): Required tolerance for convergence of Pvsat in bars. Default = 1.e-1
        nr_step (float, optional): Step size for Newton-Raphson solver for melt speciation (this can be made smaller if there are problems with convergence.). Default = 1
        nr_tol (float, optional): Tolerance for the Newton-Raphson solver for melt speciation in weight fraction (this can be made larger if there are problems with convergence). Default = 1.e-9

    Returns:
        pandas.DataFrame: Results of fO2 range from melt sulfur content calculation


    Outputs
    -------
    fO2_range_from_S: csv file (if output csv = True in models)

    """

    if last_row is None:
        last_row = len(setup)

    # run over rows in file
    for n in range(first_row, last_row, 1):  # number of rows in the table
        # Select run conditions
        run = n  # row number

        # check if any options need to be read from the setup file rather than the
        # models file
        models = options_from_setup(run, models, setup)

        PT = {"T": setup.loc[run, "T_C"]}
        melt_wf = mg.melt_comp(run, setup)

        if "P_bar" in setup:
            if setup.loc[run, "P_bar"] > 0.0:
                PT["P"] = setup.loc[run, "P_bar"]
                melt_wf["Fe3FeT"] = setup.loc[run, "Fe3FeT"]
                sulfsat_results = c.fO2_range_from_S(PT, melt_wf, models)
                sulfsat_results["P_sat_sulf"] = setup.loc[run, "P_bar"]
                sulfsat_results["P_sat_anh"] = setup.loc[run, "P_bar"]
            else:
                sulfsat_results = c.P_sat_sulf_anh(
                    PT, melt_wf, models, p_tol, nr_step, nr_tol
                )
        else:
            sulfsat_results = c.P_sat_sulf_anh(
                PT, melt_wf, models, p_tol, nr_step, nr_tol
            )

        # create results
        results_headers_table_sample_name, results_values_table_sample_name = (
            results_table_sample_name(setup, run)
        )
        results_headers_table_model_options, results_values_table_model_options = (
            results_table_model_options(models)
        )
        results_headers_T, results_values_T = (
            pd.DataFrame([["T_C"]]),
            pd.DataFrame([[PT["T"]]]),
        )
        results_headers_table_melt_vol = (
            results_table_melt_vol()
        )  # "H2OT-eq_wtpc","CO2T-eq_ppmw","ST_ppmw","X_ppmw"
        results_values_table_melt_vol = pd.DataFrame(
            [
                [
                    melt_wf["H2OT"] * 100.0,
                    melt_wf["CO2"] * 1000000.0,
                    melt_wf["ST"] * 1000000.0,
                    melt_wf["X"] * 1000000.0,
                ]
            ]
        )
        results_headers_table_sulfsat = pd.DataFrame(
            [
                [
                    "SCSS_ppm",
                    "sulfide saturated",
                    "P_bar_sulf",
                    "fO2_DFMQ_sulf",
                    "fO2_bar_sulf",
                    "Fe3+/FeT_sulf",
                    "S6+/ST_sulf",
                    "SCAS_ppm",
                    "anhydrite saturated",
                    "P_bar_anh",
                    "fO2_DFMQ_anh",
                    "fO2_bar_anh",
                    "Fe3+/FeT_anh",
                    "S6+/ST_anh",
                ]
            ]
        )
        results_values_table_sulfsat = pd.DataFrame(
            [
                [
                    sulfsat_results["SCSS"],
                    sulfsat_results["sulf_sat"],
                    sulfsat_results["P_sat_sulf"],
                    sulfsat_results["DFMQ_sulf"],
                    sulfsat_results["fO2_sulf"],
                    sulfsat_results["Fe3T_sulf"],
                    sulfsat_results["S6T_sulf"],
                    sulfsat_results["SCAS"],
                    sulfsat_results["anh_sat"],
                    sulfsat_results["P_sat_anh"],
                    sulfsat_results["DFMQ_anh"],
                    sulfsat_results["fO2_anh"],
                    sulfsat_results["Fe3T_anh"],
                    sulfsat_results["S6T_anh"],
                ]
            ]
        )
        results_headers = pd.concat(
            [
                results_headers_table_sample_name,
                results_headers_T,
                results_headers_table_melt_vol,
                results_headers_table_sulfsat,
                results_headers_table_model_options,
            ],
            axis=1,
        )
        results1 = pd.concat(
            [
                results_values_table_sample_name,
                results_values_T,
                results_values_table_melt_vol,
                results_values_table_sulfsat,
                results_values_table_model_options,
            ],
            axis=1,
        )

        if n == first_row:
            results = pd.concat([results_headers, results1])
        else:
            results = pd.concat([results, results1])

        if models.loc["print status", "option"] == "True":
            print(
                n,
                setup.loc[run, "Sample"],
                sulfsat_results["sulf_sat"],
                sulfsat_results["anh_sat"],
            )

    results.columns = results.iloc[0]
    results = results[1:]
    results.reset_index(drop=True, inplace=True)

    if models.loc["output csv", "option"] == "True":
        results.to_csv("fO2_range_from_S.csv", index=False, header=True)

    return results


# function to calculate the SCSS and SCAS with varying melt composition
def calc_sulfur_vcomp(setup, models=mdv.default_models):
    """Calculates SCAS, SCSS, Csulfide and Csulfate for multiple melt compositions

    Args:
        setup (pandas.DataFrame): Input data
        models (pandas.DataFrame, optional): Model options. Defaults to mdv.default_models.

    Returns:
        pandas.DataFrame: SCAS, SCSS, Csulfide and Csulfate for multiple melt
        compositions
    """
    for n in range(0, len(setup), 1):
        melt_wf = mg.melt_comp(n, setup)
        PT = {"T": setup.loc[n, "T_C"], "P": setup.loc[n, "P_bar"]}
        P = int(PT["P"])
        T = int(PT["T"])
        melt_wf["Fe3FeT"] = melt_wf["Fe3FeT_i"]
        fO2 = mdv.f_O2(PT, melt_wf, models)
        FMQ = mg.fO22Dbuffer(PT, fO2, "FMQ", models)
        sulfsat = c.sulfur_saturation(PT, melt_wf, models)
        sulfide_capacity = mdv.C_S(PT, melt_wf)
        sulfate_capacity = mdv.C_SO4(PT, melt_wf)
        # result = {"SCSS":SCSS_,"StCSS":StCSS,"sulfide_sat":sulfide_sat, "SCAS":SCAS_,
        # "StCAS":StCAS,"sulfate_sat":sulfate_sat,"ST":ST}
        results1 = pd.DataFrame(
            [
                [
                    P,
                    T,
                    FMQ,
                    sulfsat["SCSS"],
                    sulfsat["StCSS"],
                    sulfsat["SCAS"],
                    sulfsat["StCAS"],
                    setup.loc[n, "MgO"],
                    sulfide_capacity,
                    sulfate_capacity,
                ]
            ]
        )
        if n == 0.0:
            results_headers = pd.DataFrame(
                [
                    [
                        "P",
                        "T",
                        "FMQ",
                        "SCSS",
                        "StCSS",
                        "SCAS",
                        "StCAS",
                        "MgO",
                        "Csulfide",
                        "Csulfate",
                    ]
                ]
            )
            results = pd.concat([results_headers, results1])
        else:
            results = pd.concat([results, results1])
    results.columns = results.iloc[0]
    results = results[1:]
    return results


########################################
# measured parameters within error #####
########################################
def calc_comp_error(setup, run, iterations=100, models=mdv.default_models):
    """Generates a specified number of random melt compositions given errors on the
    composition.

    Args:
        setup (pandas.DataFrame): Input data of melt compositions and 1sd uncertainties. Assumed 1sd uncertainties are absolute unless sd_type is specified (A = absolute, R = relative).
        run (int): Row number of input data
        iterations (int, optional): Number of compositions within error to produce. Defaults to 100
        models (pandas.DataFrame, optional): Model options. Defaults to mdv.default_models.

    Returns:
        pandas.DataFrame: Results of Monte Carlo compositions

    Outputs
    -------
    'random_compositions.csv' if 'output csv' is True
    """
    sd = {}
    sd_type = {}

    for x in ["Fe3FeT", "S6ST", "DNNO", "DFMQ", "log_fO2"]:
        if x in setup:
            fO2_opt = x
            if x in ["Fe3FeT", "S6ST", "log_fO2"]:
                fO2_opt_i = x + "_i"
            else:
                fO2_opt_i = x

    if "FeO" in setup:
        Fe_opt = "FeO"
        fO2_opt = "Fe2O3"
        fO2_opt_i = "Fe2O3"
    else:
        if "FeOT" in setup:
            Fe_opt = "FeOT"
        elif "Fe2O3T" in setup:
            Fe_opt = "Fe2O3T"

    sd[Fe_opt] = setup.loc[run, Fe_opt + "_sd"]
    if Fe_opt + "_sd_type" in setup:
        sd_type[Fe_opt] = setup.loc[run, Fe_opt + "_sd_type"]
    else:
        sd_type[Fe_opt] = "A"
    sd[fO2_opt] = setup.loc[run, fO2_opt + "_sd"]
    if fO2_opt + "_sd_type" in setup:
        sd_type[fO2_opt] = setup.loc[run, fO2_opt + "_sd_type"]
    else:
        sd_type[fO2_opt] = "A"

    for x in [
        "SiO2",
        "TiO2",
        "Al2O3",
        "MnO",
        "MgO",
        "CaO",
        "Na2O",
        "K2O",
        "P2O5",
        "H2O",
        "CO2ppm",
        "Xppm",
        "STppm",
        "T_C",
    ]:
        if x + "_sd" in setup:
            sd[x] = setup.loc[run, x + "_sd"]
        else:
            sd[x] = ""
        if x + "_sd_type" in setup:
            sd_type[x] = setup.loc[run, Fe_opt + "_sd_type"]
        else:
            if x + "_sd" in setup:
                sd_type[x] = "A"
            else:
                sd_type[x] = ""

    # set up results table
    results = pd.DataFrame(
        [
            [
                "Sample",
                "T_C",
                "SiO2",
                "TiO2",
                "Al2O3",
                Fe_opt,
                "MnO",
                "MgO",
                "CaO",
                "Na2O",
                "K2O",
                "P2O5",
                "H2O",
                "CO2ppm",
                "Xppm",
                "STppm",
                fO2_opt,
            ]
        ]
    )

    melt_comp = mg.melt_comp(run, setup)

    results1 = pd.DataFrame(
        [
            [
                setup.loc[run, "Sample"],
                setup.loc[run, "T_C"],
                melt_comp["SiO2"],
                melt_comp["TiO2"],
                melt_comp["Al2O3"],
                melt_comp[Fe_opt],
                melt_comp["MnO"],
                melt_comp["MgO"],
                melt_comp["CaO"],
                melt_comp["Na2O"],
                melt_comp["K2O"],
                melt_comp["P2O5"],
                melt_comp["H2OT"] * 100.0,
                melt_comp["CO2"] * 100000.0,
                melt_comp["X"] * 1000000.0,
                melt_comp["ST"] * 1000000,
                melt_comp[fO2_opt_i],
            ]
        ]
    )

    results = pd.concat([results, results1], ignore_index=True)
    results1 = pd.DataFrame(
        [
            [
                "sds",
                "",
                sd["SiO2"],
                sd["TiO2"],
                sd["Al2O3"],
                sd[Fe_opt],
                sd["MnO"],
                sd["MgO"],
                sd["CaO"],
                sd["Na2O"],
                sd["K2O"],
                sd["P2O5"],
                sd["H2O"],
                sd["CO2ppm"],
                sd["Xppm"],
                sd["STppm"],
                sd[fO2_opt],
            ]
        ]
    )

    results = pd.concat([results, results1], ignore_index=True)
    results1 = pd.DataFrame(
        [
            [
                "sd types",
                "",
                sd_type["SiO2"],
                sd_type["TiO2"],
                sd_type["Al2O3"],
                sd_type[Fe_opt],
                sd_type["MnO"],
                sd_type["MgO"],
                sd_type["CaO"],
                sd_type["Na2O"],
                sd_type["K2O"],
                sd_type["P2O5"],
                sd_type["H2O"],
                sd_type["CO2ppm"],
                sd_type["Xppm"],
                sd_type["STppm"],
                sd_type[fO2_opt],
            ]
        ]
    )

    results = pd.concat([results, results1], ignore_index=True)
    for n in range(0, iterations, 1):  # n is number of rows of data in conditions file
        results1 = c.compositions_within_error(run, setup)
        if "T_C" in results1:
            T_C_ = results1["T_C"]
        else:
            T_C_ = setup.loc[run, "T_C"]
        results1 = pd.DataFrame(
            [
                [
                    run,
                    T_C_,
                    results1["SiO2"],
                    results1["TiO2"],
                    results1["Al2O3"],
                    results1[Fe_opt],
                    results1["MnO"],
                    results1["MgO"],
                    results1["CaO"],
                    results1["Na2O"],
                    results1["K2O"],
                    results1["P2O5"],
                    results1["H2O"],
                    results1["CO2ppm"],
                    results1["Xppm"],
                    results1["STppm"],
                    results1[fO2_opt],
                ]
            ]
        )
        results = pd.concat([results, results1], ignore_index=True)

    results.columns = results.iloc[0]
    results = results[1:]
    results.reset_index()
    if models.loc["output csv", "option"] == "True":
        results.to_csv("random_compositions.csv", index=False, header=True)
    if models.loc["print status", "option"] == "True":
        print(n, setup.loc[run, "Sample"], results1["SiO2"])

    return results


def calc_comp_error_function(
    setup,
    function="calc_Pvsat",
    first_row=0,
    last_row=None,
    iterations=100,
    models=mdv.default_models,
):
    """Calculates Pvsat or fO2-from-melt-S and uncertainity based on uncertainty on
    inputted melt composition and T.

    Args:
        setup (pandas.DataFrame): Input data of melt compositions and 1sd uncertainties. Assumed 1sd uncertainties are absolute unless sd_type is specified (A = absolute, R = relative).
        function (str, optional): Which calculation - calc_pvsat or calc_melt_S_oxybarometer - to run. Defaults to "calc_pvsat".
        first_row (int, optional): First row on input file to run. Defaults to 0.
        last_row (int, optional): Last row of input file to run. Defaults to None.
        iterations (int, optional): Number of random melt compositions to produce using Monte Carlo approach to run calculations on. Defaults to 100.
        models (pandas.DataFrame, optional): Model options. Defaults to mdv.default_models.
    """

    def is_number(s):
        try:
            float(s)
            return True
        except ValueError:
            return False

    if last_row is None:
        last_row = len(setup)

    with tqdm.tqdm(total=(last_row - first_row)) as tqdmsteps:
        for n in range(first_row, last_row, 1):
            run = n
            comp = calc_comp_error(setup, run, iterations=iterations, models=models)
            if function == "calc_Pvsat":
                result = calc_Pvsat(
                    comp, models=models, first_row=4, last_row=len(comp) - 1
                )

            elif function == "calc_melt_S_oxybarometer":
                result = calc_melt_S_oxybarometer(
                    comp, first_row=4, last_row=len(comp) - 1, models=models
                )
            av_results = {}
            headers = result.columns.tolist()
            for x in headers:
                if x == "sample":
                    av_results[x] = setup.loc[run, "Sample"]
                elif x == "Date":
                    av_results[x] = result.loc[0, x]
                elif x == "sulfide saturated" or x == "anhydrite saturated":
                    if (
                        "False" in result[x].tolist()
                        and "possible" in result[x].tolist()
                    ):
                        av_results[x] = "Both"
                    else:
                        av_results[x] = result.loc[0, x]
                elif x in [
                    "P_bar_sulf",
                    "fO2_DFMQ_sulf",
                    "fO2_bar_sulf",
                    "Fe3+/FeT_sulf",
                    "S6+/ST_sulf",
                ]:
                    if av_results["sulfide saturated"] == "False":
                        av_results[x] = result.loc[0, x]
                        av_results[x + "_sd"] = ""
                    else:
                        if av_results["sulfide saturated"] == "Both":
                            result[x] = result[x].apply(pd.to_numeric, errors="coerce")
                        av_results[x] = result[x].mean()
                        av_results[x + "_sd"] = result[x].std()
                elif x in [
                    "P_bar_anh",
                    "fO2_DFMQ_anh",
                    "fO2_bar_anh",
                    "Fe3+/FeT_anh",
                    "S6+/ST_anh",
                ]:
                    if av_results["anhydrite saturated"] == "False":
                        av_results[x] = result.loc[0, x]
                        av_results[x + "_sd"] = ""
                    else:
                        if av_results["anhydrite saturated"] == "Both":
                            result[x] = result[x].apply(pd.to_numeric, errors="coerce")
                        av_results[x] = result[x].mean()
                        av_results[x + "_sd"] = result[x].std()
                elif is_number(result.loc[0, x]) is False:
                    av_results[x] = result.loc[0, x]
                else:
                    result[x] = result[x].apply(pd.to_numeric, errors="coerce")
                    av_results[x] = result[x].mean()
                    av_results[x + "_sd"] = result[x].std()
                av_results["iterations"] = iterations
                av_results_all1 = pd.DataFrame(av_results, index=[0])
            if n == first_row:
                av_results_all = av_results_all1
            else:
                av_results_all = pd.concat([av_results_all, av_results_all1])
            if models.loc["print status", "option"] == "True":
                print(iterations, setup.loc[run, "Sample"])
            tqdmsteps.update(1)

    av_results_all.reset_index(drop=True, inplace=True)
    if models.loc["output csv", "option"] == "True":
        av_results_all.to_csv(
            function + "_random_compositions.csv", index=False, header=True
        )

    return av_results_all


########################################################################################
# WORK IN PROGRESS #####################################################################
########################################################################################


# outputting model options used in the calculation
def results_isotopes_model_options(models):
    """Outputs headers and values for model options related to isotopic fractionation.

    Args:
        models (pandas.DataFrame): Model options.

    Returns:
        tuple(pandas.DataFrame,pandas.DataFrame): Headers. Values.
    """
    results_headers = pd.DataFrame(
        [
            [
                "beta_factors",
                "alpha_H2S_S",
                "alpha_SO2_SO4",
                "alpha_S_H2Sv_H2Sm",
                "alpha_C_CO2v_CO32mm",
                "alpha_C_CO2v_CO2m",
                "alpha_C_CO2v_CO2T",
                "alpha_C_COv_COm",
                "alpha_C_CH4v_CH4m",
                "alpha_H_H2Ov_H2Om",
                "alpha_H_H2Ov_OHmm",
                "alpha_H_H2v_H2m",
                "alpha_H_CH4v_CH4m",
                "alpha_H_H2Sv_H2Sm",
                "Date",
            ]
        ]
    )
    results_values = pd.DataFrame(
        [
            [
                models.loc["beta_factors", "option"],
                models.loc["alpha_H2S_S", "option"],
                models.loc["alpha_SO2_SO4", "option"],
                models.loc["alpha_S_H2Sv_H2Sm", "option"],
                models.loc["alpha_C_CO2v_CO32mm", "option"],
                models.loc["alpha_C_CO2v_CO2m", "option"],
                models.loc["alpha_C_CO2v_CO2T", "option"],
                models.loc["alpha_C_COv_COm", "option"],
                models.loc["alpha_C_CH4v_CH4m", "option"],
                models.loc["alpha_H_H2Ov_H2Om", "option"],
                models.loc["alpha_H_H2Ov_OHmm", "option"],
                models.loc["alpha_H_H2v_H2m", "option"],
                models.loc["alpha_H_CH4v_CH4m", "option"],
                models.loc["alpha_H_H2Sv_H2Sm", "option"],
                datetime.datetime.now(),
            ]
        ]
    )
    return results_headers, results_values


def results_isotopes_gas_melt(comp, run):
    """Outputs headers and values for melt and vapor composition for isotope
    fractionation calculations.

    Args:
        comp (pandas.DataFrame): Composition of the melt and vapor by species, including weight fraction of vapor.
        run (float): Index of interest.

    Returns:
        tuple(pandas.DataFrame,pandas.DataFrame): Headers. Values.
    """
    results_headers = pd.DataFrame(
        [
            [
                "xgO2_mf",
                "xgH2_mf",
                "xgH2O_mf",
                "xgS2_mf",
                "xgSO2_mf",
                "xgH2S_mf",
                "xgCO2_mf",
                "xgCO_mf",
                "xgCH4_mf",
                "xgOCS_mf",
                "H2OT_wtpc",
                "OH_wtpc",
                "H2Omol_wtpc",
                "H2_ppmw",
                "CH4_ppmw",
                "CO2T_ppmw",
                "CO2mol_ppmw",
                "CO2carb_ppmw",
                "CO_ppmw",
                "S2-_ppmw",
                "S6+_ppmw",
                "H2S_ppmw",
                "H2OT-eq_wtpc",
                "CO2T-eq_ppmw",
                "ST_ppmw",
                "wt_g_wtpc",
            ]
        ]
    )

    results_values = pd.DataFrame(
        [
            [
                comp.loc[run, "xgO2_mf"],
                comp.loc[run, "xgH2_mf"],
                comp.loc[run, "xgH2O_mf"],
                comp.loc[run, "xgS2_mf"],
                comp.loc[run, "xgSO2_mf"],
                comp.loc[run, "xgH2S_mf"],
                comp.loc[run, "xgCO2_mf"],
                comp.loc[run, "xgCO_mf"],
                comp.loc[run, "xgCH4_mf"],
                comp.loc[run, "xgOCS_mf"],
                comp.loc[run, "H2OT_wtpc"],
                comp.loc[run, "OH_wtpc"],
                comp.loc[run, "H2Omol_wtpc"],
                comp.loc[run, "H2_ppmw"],
                comp.loc[run, "CH4_ppmw"],
                comp.loc[run, "CO2T_ppmw"],
                comp.loc[run, "CO2mol_ppmw"],
                comp.loc[run, "CO2carb_ppmw"],
                comp.loc[run, "CO_ppmw"],
                comp.loc[run, "S2-_ppmw"],
                comp.loc[run, "S6+_ppmw"],
                comp.loc[run, "H2S_ppmw"],
                comp.loc[run, "H2OT-eq_wtpc"],
                comp.loc[run, "CO2T-eq_ppmw"],
                comp.loc[run, "ST_ppmw"],
                comp.loc[run, "wt_g_wtpc"],
            ]
        ]
    )
    return results_headers, results_values


def results_table_isotopes(
    PT, R_all_species_S, R_m_g_S, R_all_species_C, R_m_g_C, R_all_species_H, R_m_g_H
):
    """Outputs headers and values for isotope ratios for all species and melt and vapor
    for all elements.

    Args:
        PT (dict): Pressure (bars) as "P" and temperature ('C) as "T".
        R_all_species_S (dict): S isotope ratios of all S-bearing species.
        R_m_g_S (dict): S isotope ratio of melt and vapor.
        R_all_species_C (dict): C isotope ratios of all C-bearing species.
        R_m_g_C (dict): C isotope ratio of melt and vapor.
        R_all_species_H (dict): H isotope ratios of all H-bearing species.
        R_m_g_H (dict): H isotope ratio of melt and vapor.

    Returns:
        tuple(pandas.DataFrame,pandas.DataFrame): Headers. Values.
    """
    results_headers = pd.DataFrame(
        [
            [
                "T_C",
                "P_bar",
                "R_S_m_tot",
                "R_S_g_tot",
                "R_H_m_tot",
                "R_H_g_tot",
                "R_C_m_tot",
                "R_C_g_tot",
                "R_S_m_S2-",
                "R_S_m_S6+",
                "R_S_m_H2S",
                "R_S_g_H2S",
                "R_S_g_SO2",
                "R_S_g_S2",
                "R_S_g_OCS",
                "R_H_m_H2O",
                "R_H_m_H2S",
                "R_H_m_CH4",
                "R_H_m_OH",
                "R_H_g_H2O",
                "R_H_g_H2S",
                "R_H_g_H2",
                "R_H_g_CH4",
                "R_C_m_CO2",
                "R_C_m_CO2carb",
                "R_C_m_CO",
                "R_C_m_CH4",
                "R_C_g_CO2",
                "R_C_g_CO",
                "R_C_g_CH4",
                "R_C_g_OCS",
            ]
        ]
    )
    results_values = pd.DataFrame(
        [
            [
                PT["T"],
                PT["P"],
                R_m_g_S["R_m"],
                R_m_g_S["R_g"],
                R_m_g_H["R_m"],
                R_m_g_H["R_g"],
                R_m_g_C["R_m"],
                R_m_g_C["R_g"],
                R_all_species_S["m_S2-"],
                R_all_species_S["m_SO42-"],
                R_all_species_S["m_H2Smol"],
                R_all_species_S["g_H2S"],
                R_all_species_S["g_SO2"],
                R_all_species_S["g_S2"],
                R_all_species_S["g_OCS"],
                R_all_species_H["m_H2Omol"],
                R_all_species_H["m_H2Smol"],
                R_all_species_H["m_CH4mol"],
                R_all_species_H["m_OH-"],
                R_all_species_H["g_H2O"],
                R_all_species_H["g_H2S"],
                R_all_species_H["g_H2"],
                R_all_species_H["g_CH4"],
                R_all_species_C["m_CO2mol"],
                R_all_species_C["m_CO32-"],
                R_all_species_C["m_COmol"],
                R_all_species_C["m_CH4mol"],
                R_all_species_C["g_CO2"],
                R_all_species_C["g_CO"],
                R_all_species_C["g_CH4"],
                R_all_species_C["g_OCS"],
            ]
        ]
    )
    return results_headers, results_values


def results_table_isotopes_d(
    R_all_species_S, R_m_g_S, R_all_species_C, R_m_g_C, R_all_species_H, R_m_g_H
):
    """Outputs headers and values for isotope ratios for all species and melt and vapor
    for all elements as delta-values.

    Args:
        R_all_species_S (dict): S isotope ratios of all S-bearing species.
        R_m_g_S (dict): S isotope ratio of melt and vapor.
        R_all_species_C (dict): C isotope ratios of all C-bearing species.
        R_m_g_C (dict): C isotope ratio of melt and vapor.
        R_all_species_H (dict): H isotope ratios of all H-bearing species.
        R_m_g_H (dict): H isotope ratio of melt and vapor.

    Returns:
        tuple(pandas.DataFrame,pandas.DataFrame): Headers. Values.
    """
    results_headers = pd.DataFrame(
        [
            [
                "d34S_m_tot",
                "d34S_g_tot",
                "dD_m_tot",
                "dD_g_tot",
                "d13C_m_tot",
                "d13C_g_tot",
                "d34S_m_S2-",
                "d34S_m_S6+",
                "d34S_m_H2S",
                "d34S_g_H2S",
                "d34S_g_SO2",
                "d34S_g_S2",
                "d34S_g_OCS",
                "dD_m_H2O",
                "dD_m_H2S",
                "dD_m_CH4",
                "dD_m_OH",
                "dD_g_H2O",
                "dD_g_H2S",
                "dD_g_H2",
                "dD_g_CH4",
                "d13C_m_CO2",
                "d13C_m_CO2carb",
                "d13C_m_CO",
                "d13C_m_CH4",
                "d13C_g_CO2",
                "d13C_g_CO",
                "d13C_g_CH4",
                "d13C_g_OCS",
            ]
        ]
    )
    results_values = pd.DataFrame(
        [
            [
                iso.ratio2delta("VCDT", 34, "S", R_m_g_S["R_m"]),
                iso.ratio2delta("VCDT", 34, "S", R_m_g_S["R_g"]),
                iso.ratio2delta("VSMOW", 2, "H", R_m_g_H["R_m"]),
                iso.ratio2delta("VSMOW", 2, "H", R_m_g_H["R_g"]),
                iso.ratio2delta("VPDB", 13, "C", R_m_g_C["R_m"]),
                iso.ratio2delta("VPDB", 13, "C", R_m_g_C["R_g"]),
                iso.ratio2delta("VCDT", 34, "S", R_all_species_S["m_S2-"]),
                iso.ratio2delta("VCDT", 34, "S", R_all_species_S["m_SO42-"]),
                iso.ratio2delta("VCDT", 34, "S", R_all_species_S["m_H2Smol"]),
                iso.ratio2delta("VCDT", 34, "S", R_all_species_S["g_H2S"]),
                iso.ratio2delta("VCDT", 34, "S", R_all_species_S["g_SO2"]),
                iso.ratio2delta("VCDT", 34, "S", R_all_species_S["g_S2"]),
                iso.ratio2delta("VCDT", 34, "S", R_all_species_S["g_OCS"]),
                iso.ratio2delta("VSMOW", 2, "H", R_all_species_H["m_H2Omol"]),
                iso.ratio2delta("VSMOW", 2, "H", R_all_species_H["m_H2Smol"]),
                iso.ratio2delta("VSMOW", 2, "H", R_all_species_H["m_CH4mol"]),
                iso.ratio2delta("VSMOW", 2, "H", R_all_species_H["m_OH-"]),
                iso.ratio2delta("VSMOW", 2, "H", R_all_species_H["g_H2O"]),
                iso.ratio2delta("VSMOW", 2, "H", R_all_species_H["g_H2S"]),
                iso.ratio2delta("VSMOW", 2, "H", R_all_species_H["g_H2"]),
                iso.ratio2delta("VSMOW", 2, "H", R_all_species_H["g_CH4"]),
                iso.ratio2delta("VPDB", 13, "C", R_all_species_C["m_CO2mol"]),
                iso.ratio2delta("VPDB", 13, "C", R_all_species_C["m_CO32-"]),
                iso.ratio2delta("VPDB", 13, "C", R_all_species_C["m_COmol"]),
                iso.ratio2delta("VPDB", 13, "C", R_all_species_C["m_CH4mol"]),
                iso.ratio2delta("VPDB", 13, "C", R_all_species_C["g_CO2"]),
                iso.ratio2delta("VPDB", 13, "C", R_all_species_C["g_CO"]),
                iso.ratio2delta("VPDB", 13, "C", R_all_species_C["g_CH4"]),
                iso.ratio2delta("VPDB", 13, "C", R_all_species_C["g_OCS"]),
            ]
        ]
    )
    return results_headers, results_values


def calc_isotopes_gassing(
    setup,
    R_i_d,
    first_row=0,
    last_row=None,
    nr_step=1.0,
    nr_tol=1.0e-9,
    models=mdv.default_models,
):
    """Calculates the isotopic ratio and delta value of all species and melt and vapor
    during degassing.

    Args:
        setup (pandas.DataFrame): Output from a degassing calculation.
        R_i_d (dict): Bulk isotope ratios as delta values.
        first_row (int, optional): First row in setup to run. Defaults to 0.
        last_row (_type_, optional): Last run in setup to run. Defaults to None.
        nr_step (float, optional): Step-size for Newton-Raphson solver. Defaults to 1.0.
        nr_tol (float, optional): Tolerance for Newton-Raphson solver. Defaults to 1.0e-9.
        models (pandas.DataFrame, optional): Model options. Defaults to mdv.default_models.

    Returns:
        pandas.DataFrame: Results of isotopic fractionation during degassing.
    """
    if last_row is None:
        last_row = len(setup)

    R_i = {}
    R_i["C"] = iso.delta2ratio("VPDB", 13, "C", R_i_d["d13C"])
    R_i["H"] = iso.delta2ratio("VSMOW", 2, "H", R_i_d["dD"])
    R_i["S"] = iso.delta2ratio("VCDT", 34, "S", R_i_d["d34S"])

    for run in range(first_row, last_row, 1):
        PT = {"P": setup.loc[run, "P_bar"]}
        PT["T"] = setup.loc[run, "T_C"]

        R_all_species_S, R_m_g_S, R_all_species_C, R_m_g_C, R_all_species_H, R_m_g_H = (
            c.calc_isotopes(PT, setup, R_i, models, nr_step, nr_tol, run=run)
        )

        iso_headers, iso_values = results_table_isotopes(
            PT,
            R_all_species_S,
            R_m_g_S,
            R_all_species_C,
            R_m_g_C,
            R_all_species_H,
            R_m_g_H,
        )

        chem_headers, chem_values = results_isotopes_gas_melt(setup, run)

        opt_headers, opt_values = results_isotopes_model_options(models)

        iso_d_headers, iso_d_values = results_table_isotopes_d(
            R_all_species_S, R_m_g_S, R_all_species_C, R_m_g_C, R_all_species_H, R_m_g_H
        )

        all_values = pd.concat(
            [iso_values, iso_d_values, chem_values, opt_values], axis=1
        )

        if run == first_row:
            all_headers = pd.concat(
                [iso_headers, iso_d_headers, chem_headers, opt_headers], axis=1
            )
            results = pd.concat([all_headers, all_values])
        else:
            results = pd.concat([results, all_values])

        if models.loc["gassing_style", "option"] == "open":
            R_i["C"] = R_m_g_C["R_m"]
            R_i["H"] = R_m_g_H["R_m"]
            R_i["S"] = R_m_g_S["R_m"]

    results.columns = results.iloc[0]
    results = results[1:]
    results.reset_index(drop=True, inplace=True)
    if models.loc["output csv", "option"] == "True":
        results.to_csv("results_gassing_isotopes.csv", index=False, header=True)

    if models.loc["print status", "option"] == "True":
        print("done", datetime.datetime.now())
    return results
