I have a project idea that I'd like you to help me turn into a comprehensive Product Requirements Document (PRD). Here's my concept:

<concept>
I need a locally-hosted webapp to view and tag or rename image files (from an arbitrary location in the local filesystem).

Display thumbnails for a page of images (either scroll or pagination to view more)
Allow for sinlge-image selection (Default mode) or multiple selection with check-marks on the thumbnails
Select a prefix and/or suffix
Select one or more pre-propulated tags ("comics", "nancy", "popart", "warhol", "fineart", "advertising", "logos", etc.)
User should be able to "add" new tags, which should be saved locally and re-used in the next session
Select a numbering system for duplicates (this could be on/off with no user options - defaulting to `000` )
App will rename the file using tags in a specified orger (alphabetical, probably?), check for existing names, and rename

For example, if the user selectes `monochrome_image.2025.10.27162055_transparent.png` with a prefix of `monochrome` and the tags ['nancy', 'comics', 'sluggo', 'food'] the file will be renamed as `monochrome_comics_food_nancy_sluggo_000.png`
</concept>


guide me through this process by asking me 2-3 focused questions for each section, one section at a time. Make the questions specific and actionable.  Wait for my response before moving to the next section. When complete, synthesise the information into a well-structured PRD format. 


## 1. Executive Summary
- Brief overview of the product
- Key value proposition
- Target market

## 2. Problem Statement
- What problem does this solve?
- Current pain points and user frustrations
- Market opportunity

## 3. Product Vision & Goals
- Long-term vision for the product
- Key objectives and success metrics
- How this fits into the broader market

## 4. Target Users & Personas
- Primary user segments
- User personas with demographics, goals, and pain points
- User journey mapping

## 5. Functional Requirements
- Core features (MVP)
- Advanced features (future releases)
- User stories with acceptance criteria

## 6. Technical Requirements
- Platform considerations
- Performance requirements
- Security and compliance needs
- Integration requirements

## 7. Design & UX Considerations
- Key design principles
- User experience goals
- Accessibility requirements

## 8. Success Metrics & KPIs
- How we'll measure product success
- Key performance indicators
- Analytics and tracking requirements

## 9. Timeline & Milestones
- Development phases
- Key deliverables and dates
- Dependencies and risks

## 10. Assumptions & Constraints
- Key assumptions we're making
- Budget, timeline, or technical constraints
- Risks and mitigation strategies

For each section, be specific and actionable. Include examples where helpful, and ask clarifying questions if you need more information about any aspect of the project. The PRD will be saved as a markdown document in `docs/plans/`