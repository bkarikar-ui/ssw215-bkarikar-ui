document.addEventListener('DOMContentLoaded', () => {
  const filterInput = document.getElementById('filter-input');
  const cards = Array.from(document.querySelectorAll('.card'));
  const countElement = document.getElementById('project-count');
  const totalProjects = cards.length;

  const updateProjects = () => {
    const query = filterInput.value.trim().toLowerCase();
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

  updateProjects();

  document.querySelectorAll('.upvote-btn').forEach((button) => {
    button.addEventListener('click', async () => {
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
        card.querySelector('.like-count').textContent = data.likes;
      } catch (error) {
        console.error('Unable to upvote project:', error);
      }
    });
  });
});
