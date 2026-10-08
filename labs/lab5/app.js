document.addEventListener('DOMContentLoaded', () => {
  const filterInput = document.getElementById('filter-input');
  const cards = Array.from(document.querySelectorAll('.card'));
  const countElement = document.getElementById('project-count');
  const totalProjects = cards.length;

  const updateProjects = () => {
    const query = filterInput.value.trim().toLowerCase();
    let visibleCount = 0;

    cards.forEach((card) => {
      const cardText = card.textContent.toLowerCase();
      const matches = query === '' || cardText.includes(query);

      card.classList.toggle('hidden', !matches);

      if (matches) {
        visibleCount += 1;
      }
    });

    countElement.textContent = `Showing ${visibleCount} of ${totalProjects} projects`;
  };

  if (filterInput) {
    filterInput.addEventListener('input', updateProjects);
  }

  updateProjects();
});
