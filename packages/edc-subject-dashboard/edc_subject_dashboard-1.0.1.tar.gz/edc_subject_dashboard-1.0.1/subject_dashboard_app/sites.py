from edc_sites.single_site import SingleSite

__all__ = ["all_sites"]

suffix = "clinicedc.org"

all_sites = [
    SingleSite(
        110,
        "capetown",
        title="UCT: Khayelitsha and Mitchell’s Plain (Cape Town)",
        country="south_africa",
        country_code="sa",
        language_codes=["en"],
        domain=f"capetown.sa.{suffix}",
    ),
    SingleSite(
        120,
        "baragwanath",
        title="Wits: Chris Hani Baragwanath (Soweto)",
        country="south_africa",
        country_code="sa",
        language_codes=["en"],
        domain=f"baragwanath.sa.{suffix}",
    ),
    SingleSite(
        130,
        "helen_joseph",
        title="Wits: Helen Joseph (Johannesburg)",
        country="south_africa",
        country_code="sa",
        language_codes=["en"],
        domain=f"helen-joseph.sa.{suffix}",
    ),
    SingleSite(
        140,
        "tshepong",
        title="Wits: Tshepong (Klerksdorp)",
        country="south_africa",
        country_code="sa",
        language_codes=["en"],
        domain=f"tshepong.sa.{suffix}",
    ),
]
