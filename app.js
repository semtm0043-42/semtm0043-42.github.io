if (typeof window.renderMathInElement === 'function') {
  window.renderMathInElement(document.body, {
    delimiters: [
      { left: '\\[', right: '\\]', display: true },
      { left: '\\(', right: '\\)', display: false },
    ],
    ignoredTags: ['script', 'noscript', 'style', 'textarea', 'pre', 'code', 'option'],
    throwOnError: false,
  });
}

const currentPage = window.location.pathname.split('/').pop() || 'index.html';
const phaseOnePages = [
  ['motors.html', 'Motors'],
  ['reflectance.html', 'Surface Reflectance Sensors'],
  ['odometry.html', 'Odometry'],
];
const referencePages = [
  ['stampc3-reference.html', 'StampC3 Template Code'],
  ['processing-reference.html', 'Processing Digital Twin'],
];

const navigationLink = (href, number, label, active = false, child = false) => `
  <a class="nav-item${active ? ' active' : ''}${child ? ' nav-tree-child' : ''}" href="${href}">
    <span>${number}</span>
    ${label}
  </a>`;

document.querySelectorAll('[data-course-navigation]').forEach((navigation) => {
  const phaseOneExpanded = currentPage === 'phase-1.html'
    || phaseOnePages.some(([href]) => href === currentPage);
  const phaseOneChildren = phaseOnePages.map(([href, label], index) => navigationLink(
    href,
    `1.${index + 1}`,
    label,
    href === currentPage,
    true,
  )).join('');
  const referenceExpanded = currentPage === 'system-reference.html'
    || referencePages.some(([href]) => href === currentPage);
  const referenceChildren = referencePages.map(([href, label], index) => navigationLink(
    href,
    `R.${index + 1}`,
    label,
    href === currentPage,
    true,
  )).join('');

  navigation.innerHTML = `
    <p class="nav-label">Course journey</p>
    ${navigationLink('index.html', '00', 'Course overview', currentPage === 'index.html')}
    ${navigationLink('course-introduction.html', 'Intro', 'Course Introduction', currentPage === 'course-introduction.html')}
    ${navigationLink('getting-started.html', 'Start', 'Getting Started', currentPage === 'getting-started.html')}
    ${navigationLink('select-a-project.html', 'Project', 'Select a Project', currentPage === 'select-a-project.html')}
    <div class="nav-tree-group">
      <div class="nav-tree-row">
        ${navigationLink('phase-1.html', '01', 'Characterise the robot', currentPage === 'phase-1.html')}
        <button class="nav-tree-toggle" type="button" data-nav-toggle aria-controls="phase-1-tree" aria-expanded="${phaseOneExpanded}" aria-label="${phaseOneExpanded ? 'Collapse' : 'Expand'} Phase 1 navigation">
          <span aria-hidden="true">${phaseOneExpanded ? '−' : '+'}</span>
        </button>
      </div>
      <div id="phase-1-tree" class="nav-tree-children"${phaseOneExpanded ? '' : ' hidden'}>
        ${phaseOneChildren}
      </div>
    </div>
    ${navigationLink('phase-2.html', '02', 'Update the Digital Twin', currentPage === 'phase-2.html')}
    <p class="nav-label nav-reference-label">Reference</p>
    <div class="nav-tree-group">
      <div class="nav-tree-row">
        ${navigationLink('system-reference.html', 'Ref', 'System Reference', currentPage === 'system-reference.html')}
        <button class="nav-tree-toggle" type="button" data-nav-toggle aria-controls="system-reference-tree" aria-expanded="${referenceExpanded}" aria-label="${referenceExpanded ? 'Collapse' : 'Expand'} System Reference navigation">
          <span aria-hidden="true">${referenceExpanded ? '−' : '+'}</span>
        </button>
      </div>
      <div id="system-reference-tree" class="nav-tree-children"${referenceExpanded ? '' : ' hidden'}>
        ${referenceChildren}
      </div>
    </div>
  `;
});

document.querySelectorAll('[data-nav-toggle]').forEach((toggle) => {
  toggle.addEventListener('click', () => {
    const tree = document.getElementById(toggle.getAttribute('aria-controls'));
    const expanded = toggle.getAttribute('aria-expanded') === 'true';
    toggle.setAttribute('aria-expanded', String(!expanded));
    const navigationName = toggle.getAttribute('aria-controls') === 'phase-1-tree'
      ? 'Phase 1'
      : 'System Reference';
    toggle.setAttribute('aria-label', `${expanded ? 'Expand' : 'Collapse'} ${navigationName} navigation`);
    toggle.querySelector('[aria-hidden="true"]').textContent = expanded ? '+' : '−';
    tree.hidden = expanded;
  });
});

document.querySelectorAll('[data-context-box] label, [data-context-box] textarea').forEach((control) => {
  control.remove();
});

document.querySelectorAll('[data-context-box]').forEach((box) => {
  const tabs = box.querySelectorAll('[data-context]');
  const panels = box.querySelectorAll('[data-panel]');

  tabs.forEach((tab) => tab.addEventListener('click', () => {
    const context = tab.dataset.context;
    box.classList.toggle('is-ai-route', context === 'ai');
    tabs.forEach((item) => {
      const selected = item === tab;
      item.classList.toggle('active', selected);
      item.setAttribute('aria-selected', selected);
    });
    panels.forEach((panel) => {
      const selected = panel.dataset.panel === context;
      panel.classList.toggle('active', selected);
      panel.hidden = !selected;
    });
  }));
});


const exercisesOpenByDefault = document.body.dataset.exerciseDefault === 'open';

document.querySelectorAll('.exercise-card').forEach((card) => {
  const heading = card.querySelector('.exercise-heading');
  if (!heading) return;

  heading.setAttribute('role', 'button');
  heading.setAttribute('tabindex', '0');
  heading.setAttribute('aria-expanded', String(exercisesOpenByDefault));
  card.classList.toggle('is-collapsed', !exercisesOpenByDefault);

  const toggle = () => {
    const collapsed = card.classList.toggle('is-collapsed');
    heading.setAttribute('aria-expanded', String(!collapsed));
  };

  heading.addEventListener('click', toggle);
  heading.addEventListener('keydown', (event) => {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      toggle();
    }
  });
});


const exerciseCards = [...document.querySelectorAll('.exercise-card')];
document.querySelectorAll('[data-exercise-action]').forEach((button) => {
  button.addEventListener('click', () => {
    const open = button.dataset.exerciseAction === 'open';
    exerciseCards.forEach((card) => {
      const heading = card.querySelector('.exercise-heading');
      card.classList.toggle('is-collapsed', !open);
      if (heading) heading.setAttribute('aria-expanded', String(open));
    });
  });
});
