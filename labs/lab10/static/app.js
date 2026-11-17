document.addEventListener('DOMContentLoaded', () => {
  const filterInput = document.getElementById('filter-input');
  const countElement = document.getElementById('project-count');
  const projectsGrid = document.querySelector('.projects-grid');
  const projectForm = document.querySelector('.project-form');
  const titleInput = document.getElementById('new-title');
  const projectFormMessage = document.getElementById('project-form-message');
  const smartProjectForm = document.querySelector('.smart-project-form');
  const smartNotes = document.getElementById('smart-notes');
  const smartProjectMessage = document.getElementById('smart-project-message');
  const githubImportForm = document.getElementById('github-import-form');
  const repoOwner = document.getElementById('repo-owner');
  const repoName = document.getElementById('repo-name');
  const githubImportMessage = document.getElementById('github-import-message');
  const githubDraftPanel = document.getElementById('github-draft-panel');
  const githubFeedbackForm = document.getElementById('github-feedback-form');
  const githubFeedback = document.getElementById('github-feedback');
  const githubDraftMessage = document.getElementById('github-draft-message');
  const githubApproveButton = document.getElementById('github-approve-button');
  let githubSessionId = null;

  const updateProjects = () => {
    const query = filterInput.value.trim().toLowerCase();
    const cards = Array.from(projectsGrid.querySelectorAll('.card'));
    const totalProjects = cards.length;
    let visibleCount = 0;
    const visibleTitles = [];

    cards.forEach((card) => {
      const cardText = card.textContent.toLowerCase();
      const matches = query === '' || cardText.includes(query);

      card.classList.toggle('hidden', !matches);

      if (matches) {
        visibleCount += 1;
        visibleTitles.push(card.querySelector('h3').textContent.trim());
      }
    });

    countElement.textContent = `Showing ${visibleCount} of ${totalProjects} projects`;
    console.log('Visible projects:', visibleTitles);
  };

  filterInput.addEventListener('input', updateProjects);

  const createProjectCard = (project) => {
    const card = document.createElement('article');
    card.className = 'card';
    card.dataset.projectId = project.id;

    const title = document.createElement('h3');
    title.textContent = project.title;
    card.append(title);

    const author = document.createElement('p');
    author.textContent = project.author;
    card.append(author);

    const description = document.createElement('p');
    description.textContent = project.summary || project.description;
    card.append(description);

    if (project.technologies) {
      const technologies = document.createElement('p');
      technologies.textContent = `Technologies: ${project.technologies}`;
      card.append(technologies);
    }

    if (project.difficulty) {
      const difficulty = document.createElement('p');
      difficulty.textContent = `Difficulty: ${project.difficulty}`;
      card.append(difficulty);
    }

    if (project.likes > 10) {
      const badge = document.createElement('span');
      badge.className = 'badge';
      badge.textContent = 'Trending';
      card.append(badge);
    }

    const likes = document.createElement('p');
    likes.append('Likes: ');
    const likeCount = document.createElement('span');
    likeCount.className = 'like-count';
    likeCount.textContent = project.likes;
    likes.append(likeCount);
    card.append(likes);

    const upvoteButton = document.createElement('button');
    upvoteButton.className = 'upvote-btn';
    upvoteButton.type = 'button';
    upvoteButton.textContent = 'Upvote';
    card.append(upvoteButton);

    return card;
  };

  projectsGrid.addEventListener('click', async (event) => {
    const button = event.target.closest('.upvote-btn');
    if (!button || !projectsGrid.contains(button)) {
      return;
    }

    const card = button.closest('.card');
    const projectId = card.dataset.projectId;

    try {
      const response = await fetch(`/api/projects/${projectId}/upvote`, {
        method: 'POST',
      });
      if (!response.ok) {
        throw new Error(`Upvote request failed with status ${response.status}`);
      }

      const data = await response.json();
      if (!Number.isInteger(data.likes)) {
        throw new Error('Upvote response did not include a valid like count');
      }
      card.querySelector('.like-count').textContent = data.likes;
    } catch (error) {
      console.error('Unable to upvote project:', error);
    }
  });

  projectForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    projectFormMessage.classList.add('hidden');
    projectFormMessage.textContent = '';

    try {
      const response = await fetch('/api/projects', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title: titleInput.value }),
      });
      if (!response.ok) {
        const data = await response.json();
        if (typeof data.error === 'string') {
          projectFormMessage.textContent = data.error;
          projectFormMessage.classList.remove('hidden');
          return;
        }
        throw new Error(`Create project request failed with status ${response.status}`);
      }

      const project = await response.json();
      if (
        !Number.isInteger(project.id) ||
        typeof project.title !== 'string' ||
        typeof project.author !== 'string' ||
        typeof project.description !== 'string' ||
        !Number.isInteger(project.likes)
      ) {
        throw new Error('Create project response did not include a valid project');
      }

      projectsGrid.append(createProjectCard(project));
      titleInput.value = '';
      updateProjects();
    } catch (error) {
      projectFormMessage.textContent = 'Unable to create project. Please try again.';
      projectFormMessage.classList.remove('hidden');
      console.error('Unable to create project:', error);
    }
  });

  smartProjectForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    smartProjectMessage.classList.add('hidden');
    smartProjectMessage.textContent = '';

    try {
      const response = await fetch('/api/projects/smart', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ notes: smartNotes.value }),
      });
      if (!response.ok) {
        const data = await response.json();
        if (typeof data.error === 'string') {
          smartProjectMessage.textContent = data.error;
          smartProjectMessage.classList.remove('hidden');
          return;
        }
        throw new Error(`Smart create request failed with status ${response.status}`);
      }

      const data = await response.json();
      if (
        !Number.isInteger(data.id) ||
        typeof data.title !== 'string' ||
        typeof data.summary !== 'string' ||
        typeof data.technologies !== 'string' ||
        typeof data.author !== 'string' ||
        !Number.isInteger(data.likes)
      ) {
        throw new Error('Smart create response did not include a valid project');
      }

      projectsGrid.append(createProjectCard(data));
      smartNotes.value = '';
      updateProjects();
    } catch (error) {
      smartProjectMessage.textContent = 'Unable to create project. Please try again.';
      smartProjectMessage.classList.remove('hidden');
      console.error('Unable to smart-create project:', error);
    }
  });

  const showMessage = (element, message) => {
    element.textContent = message;
    element.classList.remove('hidden');
  };

  const showGithubDraft = (draft) => {
    const validDifficulties = ['Beginner', 'Intermediate', 'Advanced'];
    if (
      typeof draft.title !== 'string' ||
      typeof draft.summary !== 'string' ||
      !Array.isArray(draft.technologies) ||
      !draft.technologies.every((technology) => typeof technology === 'string') ||
      !validDifficulties.includes(draft.difficulty)
    ) {
      throw new Error('GitHub draft response did not include valid project details');
    }

    document.getElementById('github-draft-title').textContent = draft.title;
    document.getElementById('github-draft-summary').textContent = draft.summary;
    document.getElementById('github-draft-difficulty').textContent = draft.difficulty;

    const technologyList = document.getElementById('github-draft-technologies');
    technologyList.replaceChildren();
    draft.technologies.forEach((technology) => {
      const item = document.createElement('li');
      item.textContent = technology;
      technologyList.append(item);
    });

    githubDraftMessage.classList.add('hidden');
    githubDraftMessage.textContent = '';
    githubDraftPanel.classList.remove('hidden');
  };

  githubImportForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    githubImportMessage.classList.add('hidden');
    githubImportMessage.textContent = '';
    githubDraftPanel.classList.add('hidden');
    githubSessionId = null;

    try {
      const response = await fetch('/api/projects/git-start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ owner: repoOwner.value, repo: repoName.value }),
      });
      if (!response.ok) {
        const data = await response.json();
        showMessage(githubImportMessage, data.error || 'Unable to fetch a project draft.');
        return;
      }

      const data = await response.json();
      if (typeof data.session_id !== 'string' || !data.session_id) {
        throw new Error('GitHub import response did not include a session id');
      }
      showGithubDraft(data.draft);
      githubSessionId = data.session_id;
    } catch (error) {
      showMessage(githubImportMessage, 'Unable to fetch a project draft. Please try again.');
      console.error('Unable to start GitHub import:', error);
    }
  });

  githubFeedbackForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    githubDraftMessage.classList.add('hidden');
    githubDraftMessage.textContent = '';
    if (!githubSessionId) {
      showMessage(githubDraftMessage, 'Fetch a draft before sending feedback.');
      return;
    }

    try {
      const response = await fetch('/api/projects/git-refine', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: githubSessionId,
          feedback: githubFeedback.value,
        }),
      });
      if (!response.ok) {
        const data = await response.json();
        showMessage(githubDraftMessage, data.error || 'Unable to refine this draft.');
        return;
      }

      showGithubDraft(await response.json());
      githubFeedback.value = '';
    } catch (error) {
      showMessage(githubDraftMessage, 'Unable to refine this draft. Please try again.');
      console.error('Unable to refine GitHub draft:', error);
    }
  });

  githubApproveButton.addEventListener('click', async () => {
    githubDraftMessage.classList.add('hidden');
    githubDraftMessage.textContent = '';
    if (!githubSessionId) {
      showMessage(githubDraftMessage, 'Fetch a draft before approving it.');
      return;
    }

    try {
      const response = await fetch('/api/projects/git-commit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: githubSessionId }),
      });
      if (!response.ok) {
        const data = await response.json();
        showMessage(githubDraftMessage, data.error || 'Unable to save this project.');
        return;
      }

      const project = await response.json();
      if (
        !Number.isInteger(project.id) ||
        typeof project.title !== 'string' ||
        typeof project.author !== 'string' ||
        typeof project.summary !== 'string' ||
        typeof project.technologies !== 'string' ||
        typeof project.difficulty !== 'string' ||
        !Number.isInteger(project.likes)
      ) {
        throw new Error('Saved project response did not include a valid project');
      }

      projectsGrid.append(createProjectCard(project));
      githubDraftPanel.classList.add('hidden');
      githubSessionId = null;
      githubFeedback.value = '';
      updateProjects();
    } catch (error) {
      showMessage(githubDraftMessage, 'Unable to save this project. Please try again.');
      console.error('Unable to approve GitHub draft:', error);
    }
  });

  updateProjects();
});
