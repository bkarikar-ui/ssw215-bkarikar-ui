document.addEventListener('DOMContentLoaded', () => {
  const filterInput = document.getElementById('filter-input');
  const countElement = document.getElementById('project-count');
  const projectsGrid = document.querySelector('.projects-grid');
  const projectForm = document.querySelector('.project-form');
  const titleInput = document.getElementById('new-title');

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

    const description = document.createElement('p');
    description.textContent = project.description;
    card.append(description);

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

    try {
      const response = await fetch('/api/projects', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title: titleInput.value }),
      });
      if (!response.ok) {
        throw new Error(`Create project request failed with status ${response.status}`);
      }

      const project = await response.json();
      if (
        !Number.isInteger(project.id) ||
        typeof project.title !== 'string' ||
        typeof project.description !== 'string' ||
        !Number.isInteger(project.likes)
      ) {
        throw new Error('Create project response did not include a valid project');
      }

      projectsGrid.append(createProjectCard(project));
      titleInput.value = '';
      updateProjects();
    } catch (error) {
      console.error('Unable to create project:', error);
    }
  });

  updateProjects();
});
