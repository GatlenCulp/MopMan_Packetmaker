from airtable import airtable
import requests
from pathlib import Path
from src.template_factory import make_id_from_title
import json
import dotenv

# For mopman specifically: https://airtable.com/app6h2R2QQuhvFYVq/api/docs#javascript/metadata
env = dotenv.dotenv_values("secrets/.env")
API_KEY = env["AIRTABLE_API_KEY"]
BASE_ID = "app6h2R2QQuhvFYVq"
mopman = airtable.Airtable(BASE_ID, API_KEY)

at_map = {
    "curriculum": "📚 curriculum",
    "core_readings": "📗 core_readings",
    "further_readings": "📗 further_readings",
    "org": "🏢 org",
    "orgs": "🏢 orgs",
    "logo_master_raster": "📷 logo_master_raster",
    "color_primary": "🌈 color_primary",
    "color_primary_faded": "🌈 color_primary_faded",
    "color_secondary": "🌈 color_secondary",
    "org_logo": "🏢 org_logo",
    "meeting_i": "📚 meeting_i",
    "meeting_title": "🔑 meeting_title",
    "readings": "📗 readings",
    "author": "👨\u200d🔬 author",
    "year": "🕒 year",
    "trimmed_pdf": "📄 trimmed_pdf",
    "complete_pdf": "📄 complete_pdf",
    "title": "🔑 title",
    "subsection": "🗒 subsection",
    "thumbnail": "📷 thumbnail",
    "url": "url",
    "name": "🔑 name",
    "program_long_name": "💥 program_long_name",
    "program_name": "💥 program_name",
    "program": "💥 program",
    "programs": "💥 programs",
    "cohorts": "📣 cohorts",
    "global_cohort_i": "#️⃣ global_cohort_i",
    "num_members": "num_members",
    "packet_pdf": "📄 packet_pdf",
    "meeting_ta_guide_pdf": "📄 meeting_ta_guide_pdf",
    "base_ta_guide_pdf": "📄 base_ta_guide_pdf",
    "read_on_device": "read_on_device",
    "time_period": "🕒 time_period",
}


def getPrecontextForCurriculum(
    curriculum_id: str, output_dir: Path = Path("./precontexts")
) -> dict:
    assert isinstance(curriculum_id, str)
    assert isinstance(output_dir, Path)

    def save_from_airtable(url: str, file_path: Path) -> Path:
        assert isinstance(url, str)
        assert isinstance(file_path, Path)
        assert file_path.suffix == ""
        file_path.parent.mkdir(parents=True, exist_ok=True)
        request = requests.get(url)
        file_type = request.headers["Content-Type"].split("/")[-1]
        real_file_path = file_path.with_suffix("." + file_type)
        with open(str(real_file_path), mode="wb") as f:
            f.write(request.content)
        # if str(real_file_path) == "output/test1/precontext/aisf_ml_meeting_5__model_internals/thumbnails/emergent_world_representations_exploring_a_sequence_model_trained_on_a_synthetic_task.jpeg":
        #     print("AHHHH")
        return real_file_path

    def getFromRecord(
        record: dict,
        field: str,
        attachment_file_path: Path | None = None,
        single_attachment: bool = True,
    ) -> str | list[str]:
        assert isinstance(record, dict)
        assert isinstance(field, str)
        assert attachment_file_path is None or isinstance(attachment_file_path, Path)
        assert isinstance(single_attachment, bool)
        if at_map[field] not in record["fields"]:
            return ""
        if attachment_file_path:
            attachment_paths = [
                str(
                    save_from_airtable(
                        attachment["url"],
                        attachment_file_path.with_stem(
                            f"{attachment_file_path.stem}{i}"
                        ),
                    )
                )
                for i, attachment in enumerate(record["fields"][at_map[field]])
            ]
            if single_attachment:
                return attachment_paths[0] if attachment_paths else ""

        return record["fields"][at_map[field]]

    curriculum = mopman.get(at_map["curriculum"], curriculum_id)
    curriculum_name = getFromRecord(curriculum, "name")
    output_dir = output_dir / make_id_from_title(curriculum_name)
    output_dir.mkdir(parents=True, exist_ok=True)

    # I can feel my perfectionism about how jank this is getting in the way of me actually doing it and saving time now lol. Learn to prototype my dude.
    ## Core readings
    core_reading_ids = getFromRecord(curriculum, "core_readings")
    core_readings = [mopman.get(at_map["readings"], id) for id in core_reading_ids]
    core_readings = [
        {
            "title": getFromRecord(reading, "title"),
            "trimmed_pdf": getFromRecord(
                reading,
                "trimmed_pdf",
                attachment_file_path=output_dir
                / Path(
                    make_id_from_title(
                        getFromRecord(reading, "title")
                        + getFromRecord(reading, "subsection")
                    ),
                    single_attachment=True,
                ),
            ),
            "read_on_device": getFromRecord(reading, "read_on_device"),
            "subsection": getFromRecord(reading, "subsection"),
            "author": getFromRecord(reading, "author"),
            "year": getFromRecord(reading, "year"),
            "url": getFromRecord(reading, "url"),
            "thumbnail_path": "",
        }
        for reading in core_readings
    ]

    ## Further readings
    further_reading_ids = getFromRecord(curriculum, "further_readings")
    further_readings = [
        mopman.get(at_map["readings"], id) for id in further_reading_ids
    ]
    thumbnail_dir = output_dir / Path("thumbnails/")
    thumbnail_dir.mkdir(parents=True, exist_ok=True)
    further_readings = [
        {
            "title": getFromRecord(reading, "title"),
            "subsection": getFromRecord(reading, "subsection"),
            "author": getFromRecord(reading, "author"),
            "year": getFromRecord(reading, "year"),
            "url": getFromRecord(reading, "url"),
            "thumbnail_path": "",
            # "thumbnail_path": str(
            #     save_from_airtable(
            #         reading["fields"][at_map["thumbnail"]][0]["url"],
            #         thumbnail_dir/Path(f'{makeIDFromTitle(reading["fields"][at_map["title"]])}')
            #     )
            # )
        }
        for reading in further_readings
    ]

    ## Retrieve cohorts info
    program_id = getFromRecord(curriculum, "program")[0]
    program = mopman.get(at_map["programs"], program_id)
    cohort_ids = getFromRecord(program, "cohorts")
    cohorts = [mopman.get(at_map["cohorts"], cohort_id) for cohort_id in cohort_ids]
    cohorts = list(
        map(
            lambda cohort: {
                "name": getFromRecord(cohort, "name"),
                "global_cohort_i": getFromRecord(cohort, "global_cohort_i"),
                "num_members": getFromRecord(cohort, "num_members"),
            },
            cohorts,
        )
    )

    ## Get Org info
    org_id = getFromRecord(curriculum, "org")[0]
    org = mopman.get(at_map["orgs"], org_id)

    ## Generate context
    precontext = {
        "curriculum_name": curriculum_name,
        "logo_path": getFromRecord(
            org,
            "logo_master_raster",
            attachment_file_path=output_dir / Path("logo"),
            single_attachment=True,
        ),
        "program_long_name": getFromRecord(curriculum, "program_long_name")[0],
        "program_name": getFromRecord(curriculum, "program_name")[0],
        "time_period": getFromRecord(program, "time_period"),
        "chron_info": f'Week {curriculum["fields"][at_map["meeting_i"]]}',
        "title": curriculum["fields"][at_map["meeting_title"]],
        "subtitle": "readings",
        "core_readings": core_readings,
        "further_readings": further_readings,
        "cohorts": cohorts,
        "meeting_ta_guide_pdf": getFromRecord(
            curriculum,
            "meeting_ta_guide_pdf",
            attachment_file_path=output_dir / Path("TA Guides/meeting_ta_guide"),
            single_attachment=True,
        ),
        "base_ta_guide_pdf": getFromRecord(
            org,
            "base_ta_guide_pdf",
            attachment_file_path=output_dir / Path("TA Guides/base_ta_guide"),
            single_attachment=True,
        ),
        "color_primary": getFromRecord(org, "color_primary"),
        "color_primary_faded": getFromRecord(org, "color_primary_faded"),
        "color_secondary": getFromRecord(org, "color_secondary"),
    }

    ## Save Context
    with open(output_dir / Path("precontext.json"), "w") as outfile:
        json.dump(precontext, outfile, indent=4)

    return precontext


def upload_packet_to_curriculum(curriculum_id: str, packet_path: Path) -> None:
    assert isinstance(curriculum_id, str)
    assert isinstance(packet_path, Path)

    return


if __name__ == "__main__":
    target_curriculum_id = "reccFZa1fy2EV3qPI"
    precontext = getPrecontextForCurriculum(
        target_curriculum_id, Path("./precontexts/test1")
    )
    print(precontext)
