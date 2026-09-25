# SPEC: Developer Portfolio Welcome Page
## 1. Purpose & Scope
- A personal portfolio welcome page for Backling Karikari, a first-year software
engineering student.
- Non-Goals: no multi-page routing; no backend; no contact forms.
## 2. Invariants & Negative Constraints
- All styling MUST reside in `./style.css` (no inline style="..." attributes).
- The page MUST NOT load external CSS frameworks or CDNs (no Bootstrap, no Tailwind).
- The avatar image MUST use the relative path `./assets/avatar.jpg`.
- The layout MUST collapse into a single vertical column on screens narrower than 768px.
## 3. UI Content & Interface Contract
- Hero header: my full name Backling Karikari, the subtitle "Software engineering student passionate about technology, problem-solving, and creating solutions that help others.", and
this bio: "I’m a software engineering student who has always been interested in technology and how things work. I’m passionate about building useful software, learning new skills, and using technology to make a positive impact in my community.".
- Action link: a button labelled "See my projects" that links to `#projects`.
- Projects section with id="projects": lists these items: Built an Arduino-based robot that uses A* pathfinding to navigate a grid.
Designed a smart watering system using sensors to monitor plants.
Want to make useful software tools that help college students stay organized.
- Social link: GitHub (https://github.com/bkarikar-ui) MUST open in a new tab
(target="_blank").
- The page background MUST be dark navy (#1b2a41) with white text.
## 4. Acceptance Checklist
- [x] Valid semantic HTML5: the page uses <header>, <main>, and <footer>.
- [x] The avatar image has width, height, and alt attributes.
- [x] No horizontal scrollbar when the browser is narrowed to 375px.
- [x] The GitHub link opens in a new tab and has rel="noopener".
- [x] No placeholder links: href="#" appears nowhere.
## 5. Audit Protocol
- Inspect the generated code line by line with `git diff --staged` before committing.