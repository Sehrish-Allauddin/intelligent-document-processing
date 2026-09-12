class ProjectParser:
    PROJECT_HEADERS = {
        "projects", "project", "academic projects", "personal projects",
        "major projects", "minor projects", "portfolio projects", "key projects",
    }

    def parse(self, project_text):
        if isinstance(project_text, str):
            lines = [x.strip() for x in project_text.splitlines() if x.strip()]
        elif isinstance(project_text, list):
            lines = [str(x).strip() for x in project_text if str(x).strip()]
        else:
            return []

        projects = []
        current = None

        # A title is usually a short standalone line. We also support known
        # project-title prefixes without hard-coding the student's projects.
        known_prefixes = (
            "ai-based ", "al-based ", "fraud detection",
            "fall detection", "resume parser", "document processing",
        )

        for line in lines:
            lower = line.lower()
            if lower in self.PROJECT_HEADERS:
                continue

            is_title = lower.startswith(known_prefixes)
            if not is_title and current is None:
                # If a project section contains only one or more plain titles,
                # accept short title-like lines before descriptions.
                is_title = len(line.split()) <= 8 and not line.endswith(".")

            if is_title:
                if current is not None:
                    projects.append(current)
                current = {"title": line, "description": []}
                continue

            if current is not None:
                current["description"].append(line)

        if current is not None:
            projects.append(current)

        return projects
