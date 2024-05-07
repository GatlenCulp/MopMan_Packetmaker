config = {
    # String-based paths to templates
    "templates": {
        "cover": "templates/Cover Page Template.docx",
        "device_reading": "templates/Device Reading.docx",
        "further_reading": "templates/Further Reading.docx",
        "tas_guide": "templates/TAs Guide.docx",
    },
    "error_pdf": "templates/ERROR.pdf",
    # Where to output the generated files
    "output_dir": "output/",
    # Map of the curriculum name to the Airtable Record ID
    "curriculum_ids": {
    "AISST Intro Fellowship Spring 2024 Meeting 0 - Introduction to machine learning (optional)": "reccJl6itaZXjjOHb",
    "AISST Intro Fellowship Spring 2024 Meeting 1 - Reward misspecification, RLHF, and deception": "recU9bm11auhEbxb1",
    "AISST Intro Fellowship Spring 2024 Meeting 2 - Goals and goal misgeneralization": "recWO4Gd0XUJFumFt",
    "AISST Intro Fellowship Spring 2024 Meeting 3 - Current trajectory and risk stories": "rechrP8xAc7OoBQnO",
    "AISST Intro Fellowship Spring 2024 Meeting 4 - Mechanistic interpretability": "recmMrdRNtceQcI1x",
    "AISST Intro Fellowship Spring 2024 Meeting 5 - Model internals": "rece0XFZaiP6aORuW",
    "AISST Intro Fellowship Spring 2024 Meeting 6 - Scalable oversight": "recp1UyHI2HbcAvpm",
    "AISST Intro Fellowship Spring 2024 Meeting 7 - Red teaming": "reccIbY85lcz5VZdl",
    "AISST Intro Fellowship Spring 2024 Meeting 8 - Policy, model evaluations, and careers in alignment": "recLGAt5DcvQssi9P",

    "AISST Policy Fellowship Spring 2024 Meeting 1 - Introduction to machine learning and AI": "recTNAdOQOszEsfKs",
    "AISST Policy Fellowship Spring 2024 Meeting 2 - Overview of risks from advanced AI systems": "rec6olieB9HqJ5rAx",
    "AISST Policy Fellowship Spring 2024 Meeting 3 - Safety standards and regulations": "recORIpIJsnZl0hGw",
    "AISST Policy Fellowship Spring 2024 Meeting 4 - AI audits and evaluations": "recVn4xjpgTnZckvd",
    "AISST Policy Fellowship Spring 2024 Meeting 4 - Self and Corporate Governance": "recXjxDvM5pWfhAJ3",
    "AISST Policy Fellowship Spring 2024 Meeting 5 - Compute governance": "recrJ7k1JqKAebXSn",
    "AISST Policy Fellowship Spring 2024 Meeting 6 - International approaches to AI regulation": "recKHV7NonRIJqbzs",
    "AISST Policy Fellowship Spring 2024 Meeting 7 - Other proposals, next steps, and careers": "recFwHTB6i5Ie0UgI",

    "AISST Takeoffs Spring 2024 Meeting 1 - Intro": "recA42wzlZr6tww8R",

    "AISST AI Prediction Hackathon February 2024 Meeting 0 - Prerequisite Readings": "recr5cpGoM8Cm8byR",

    "CAIAC AISF Intro Policy Spring 2024 Meeting 1": "recmzjrcqEnsdUaZI",
    "CAIAC AISF Intro Policy Spring 2024 Meeting 2": "recBOe41fvlmFsyA3",
    "CAIAC AISF Intro Policy Spring 2024 Meeting 3": "recIzUmC1FWjmDaZs",
    "CAIAC AISF Intro Policy Spring 2024 Meeting 4": "rec0xpDkkfEtnAhec",
    "CAIAC AISF Intro Policy Spring 2024 Meeting 5": "rec1PQHRqbI03pfJC",
    "CAIAC AISF Intro Policy Spring 2024 Meeting 6": "rec3YwgqHVAnNIdSc",
    "CAIAC AISF Intro Policy Spring 2024 Meeting 7": "rec5bvBA70NfOUnPk",

    "CAIAC AISF Intro Tech Spring 2024 Meeting 1": "rechZYbOGpGEgxWUS",
    "CAIAC AISF Intro Tech Spring 2024 Meeting 2": "recJTGZbSt0pk7sL5",
    "CAIAC AISF Intro Tech Spring 2024 Meeting 3": "recSvwsOwaKVkTrtx",
    "CAIAC AISF Intro Tech Spring 2024 Meeting 4": "recNrMWq84TXhils5",
    "CAIAC AISF Intro Tech Spring 2024 Meeting 5": "rec8LvYR1zlbjxDxg",
    "CAIAC AISF Intro Tech Spring 2024 Meeting 6": "recsHd7CcjUB5z6E6",
    "CAIAC AISF Intro Tech Spring 2024 Meeting 7": "rec0UIJwNLowqybnF",

    "MAIA AISF Technical Spring 2024 Meeting 0": "recRJ7FzFzL5sD2LE",
    "MAIA AISF Technical Spring 2024 Meeting 1": "recJNPxFUBXvrAHVN",
    "MAIA AISF Technical Spring 2024 Meeting 2": "recBkKP8v8Xli6j23",
    "MAIA AISF Technical Spring 2024 Meeting 3": "recu97MCwXyf8vlwT",
    "MAIA AISF Technical Spring 2024 Meeting 4": "recx7GJ4fTtX7G7In",
    "MAIA AISF Technical Spring 2024 Meeting 5": "recPOAk9GEP3PKNm1",
    "MAIA AISF Technical Spring 2024 Meeting 6": "recDPoo8RM1B10WAA",
    "MAIA AISF Technical Spring 2024 Meeting 7": "recJaOWqslHj9yFnx",
    "MAIA AISF Technical Spring 2024 Meeting 8": "rec5sJZuXQyxaDbyC",

    "MAIA AISF Policy Spring 2024 Meeting 1 - Introduction to machine learning and AI": "recZVv1vphT2WZmhf",
    "MAIA AISF Policy Spring 2024 Meeting 2 - Overview of risks from advanced AI systems": "recziVNqgb9vfFHW1",
    "MAIA AISF Policy Spring 2024 Meeting 3 - Safety standards and regulations": "recvmipCELPA5tBiW",
    "MAIA AISF Policy Spring 2024 Meeting 4 - AI audits and evaluations": "recd3FJ8M4pY4z8vm",
    "MAIA AISF Policy Spring 2024 Meeting 4 - Self and Corporate Governance": "rec3bJbqtrhcpjYYR",
    "MAIA AISF Policy Spring 2024 Meeting 5 - Compute governance": "recrJ7k1JqKAebXSn",
    "MAIA AISF Policy Spring 2024 Meeting 6 - International approaches to AI regulation": "recnp7x1g8RmwKZFO",
    "MAIA AISF Policy Spring 2024 Meeting 7 - Other proposals, next steps, and careers": "recMtKFW5BcorOxQ9",

    'MAIA Undergrad Member Meeting Spring 2024 Meeting 1 - TBD': 'recskC5aEHeOQkyn9',
    'MAIA Undergrad Member Meeting Spring 2024 Meeting 2 - Sleeper Agents': 'recwm3otEoIiqUjIU',
    'MAIA Undergrad Member Meeting Spring 2024 Meeting 3 - TBD': 'recw1nZ0AnCeBxxv5',
    'MAIA Undergrad Member Meeting Spring 2024 Meeting 4 - TBD': 'rec3Ossv0fYovLZU6',
    'MAIA Undergrad Member Meeting Spring 2024 Meeting 5 - TBD': 'recPA69vEKgNiXYjr',
    'MAIA Undergrad Member Meeting Spring 2024 Meeting 6 - TBD': 'rec7Tq3ooTpIGsMx9',

    'MAIA Advanced Undergrad Member Meeting Spring 2024 Meeting 1 - TBD': 'recp47JVLvZYFkezG',
    'MAIA Advanced Undergrad Member Meeting Spring 2024 Meeting 2 - Sleeper Agents': 'recqTn1D4he0kWxkZ',
    'MAIA Advanced Undergrad Member Meeting Spring 2024 Meeting 3 - TBD': 'recYQNHQ4As0eP9P6',
    'MAIA Advanced Undergrad Member Meeting Spring 2024 Meeting 4 - TBD': 'recl4SmSupTZubXwx',
    'MAIA Advanced Undergrad Member Meeting Spring 2024 Meeting 5 - TBD': 'recSZrpoCFsbiI5Ei',
    'MAIA Advanced Undergrad Member Meeting Spring 2024 Meeting 6 - TBD': 'recN5t8MqkRmtJif8',

    'MAIA Grad Member Meeting Spring 2024 Meeting 1 - TBD': 'reccAZVbfoIDTjS8y',
    'MAIA Grad Member Meeting Spring 2024 Meeting 2 - TBD': 'recf6Ao4pf4pKTPrB',
    'MAIA Grad Member Meeting Spring 2024 Meeting 3 - TBD': 'recDISXClWKZhKOZ2',
    'MAIA Grad Member Meeting Spring 2024 Meeting 4 - TBD': 'recGT20Y7bEtMpF8I',
    'MAIA Grad Member Meeting Spring 2024 Meeting 5 - TBD': 'recw6Gj8BGeN2wqcZ',
    'MAIA Grad Member Meeting Spring 2024 Meeting 6 - TBD': 'recqkctbEtGV9y8bl'


},
    # Include names of the curriculum above
    "curriculum_to_generate": [
        # "AISST Intro Fellowship Spring 2024 Meeting 0 - Introduction to machine learning (optional)",
        # "AISST Intro Fellowship Spring 2024 Meeting 1 - Reward misspecification, RLHF, and deception",
        # "AISST Intro Fellowship Spring 2024 Meeting 2 - Goals and goal misgeneralization",
        # "AISST Intro Fellowship Spring 2024 Meeting 3 - Current trajectory and risk stories",
        # "AISST Intro Fellowship Spring 2024 Meeting 4 - Mechanistic interpretability",
        # "AISST Intro Fellowship Spring 2024 Meeting 5 - Model internals",
        # "AISST Intro Fellowship Spring 2024 Meeting 6 - Scalable oversight",
        # "AISST Intro Fellowship Spring 2024 Meeting 7 - Red teaming",
        # "AISST Intro Fellowship Spring 2024 Meeting 8 - Policy, model evaluations, and careers in alignment"

        # "AISST Policy Fellowship Spring 2024 Meeting 1 - Introduction to machine learning and AI",
        # "AISST Policy Fellowship Spring 2024 Meeting 2 - Overview of risks from advanced AI systems",
        # "AISST Policy Fellowship Spring 2024 Meeting 3 - Safety standards and regulations",
        # "AISST Policy Fellowship Spring 2024 Meeting 4 - AI audits and evaluations",
        # "AISST Policy Fellowship Spring 2024 Meeting 4 - Self and Corporate Governance",
        # "AISST Policy Fellowship Spring 2024 Meeting 5 - Compute governance",
        # "AISST Policy Fellowship Spring 2024 Meeting 6 - International approaches to AI regulation",
        # "AISST Policy Fellowship Spring 2024 Meeting 7 - Other proposals, next steps, and careers",

        # "AISST Takeoffs Spring 2024 Meeting 1 - Intro",

        # "AISST AI Prediction Hackathon February 2024 Meeting 0 - Prerequisite Readings",

        # "MAIA AISF Technical Spring 2024 Meeting 0",
        # "MAIA AISF Technical Spring 2024 Meeting 1",
        # "MAIA AISF Technical Spring 2024 Meeting 2",
        # "MAIA AISF Technical Spring 2024 Meeting 3",
        # "MAIA AISF Technical Spring 2024 Meeting 4",
        # "MAIA AISF Technical Spring 2024 Meeting 5",
        # "MAIA AISF Technical Spring 2024 Meeting 6",
        # "MAIA AISF Technical Spring 2024 Meeting 7",
        # "MAIA AISF Technical Spring 2024 Meeting 8",

        # "MAIA AISF Policy Spring 2024 Meeting 1 - Introduction to machine learning and AI",
        # "MAIA AISF Policy Spring 2024 Meeting 2 - Overview of risks from advanced AI systems",
        # "MAIA AISF Policy Spring 2024 Meeting 3 - Safety standards and regulations",
        # "MAIA AISF Policy Spring 2024 Meeting 4 - AI audits and evaluations",
        "MAIA AISF Policy Spring 2024 Meeting 4 - Self and Corporate Governance",
        # "MAIA AISF Policy Spring 2024 Meeting 5 - Compute governance",
        # "MAIA AISF Policy Spring 2024 Meeting 6 - International approaches to AI regulation",
        # "MAIA AISF Policy Spring 2024 Meeting 7 - Other proposals, next steps, and careers",

        # 'MAIA Undergrad Member Meeting Spring 2024 Meeting 1 - TBD',
        # 'MAIA Undergrad Member Meeting Spring 2024 Meeting 2 - Sleeper Agents',
        # 'MAIA Undergrad Member Meeting Spring 2024 Meeting 3 - TBD',
        # 'MAIA Undergrad Member Meeting Spring 2024 Meeting 4 - TBD',
        # 'MAIA Undergrad Member Meeting Spring 2024 Meeting 5 - TBD',
        # 'MAIA Undergrad Member Meeting Spring 2024 Meeting 6 - TBD',

        # 'MAIA Advanced Undergrad Member Meeting Spring 2024 Meeting 1 - TBD',
        # 'MAIA Advanced Undergrad Member Meeting Spring 2024 Meeting 2 - Sleeper Agents',
        # 'MAIA Advanced Undergrad Member Meeting Spring 2024 Meeting 3 - TBD',
        # 'MAIA Advanced Undergrad Member Meeting Spring 2024 Meeting 4 - TBD',
        # 'MAIA Advanced Undergrad Member Meeting Spring 2024 Meeting 5 - TBD',
        # 'MAIA Advanced Undergrad Member Meeting Spring 2024 Meeting 6 - TBD',

        # 'MAIA Grad Member Meeting Spring 2024 Meeting 1 - TBD',
        # 'MAIA Grad Member Meeting Spring 2024 Meeting 2 - TBD',
        # 'MAIA Grad Member Meeting Spring 2024 Meeting 3 - TBD',
        # 'MAIA Grad Member Meeting Spring 2024 Meeting 4 - TBD',
        # 'MAIA Grad Member Meeting Spring 2024 Meeting 5 - TBD',
        # 'MAIA Grad Member Meeting Spring 2024 Meeting 6 - TBD'
    ],
    # Whether to generate parts of the curriculum
    "generate": {
        "cover": True,
        "device_readings": True,
        "further_readings": True,
        "packet": True,
        "tas_guides": False,
    }
}