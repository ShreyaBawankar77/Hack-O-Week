const toast = document.getElementById('toast');
const toastText = document.getElementById('toastText');
let timer;
function notify(message) {
  toastText.textContent = message;
  toast.classList.add('show');
  clearTimeout(timer);
  timer = setTimeout(() => toast.classList.remove('show'), 3200);
}
document.querySelectorAll('[data-view]').forEach(button => button.addEventListener('click', () => {
  document.querySelectorAll('.nav-item').forEach(item => item.classList.remove('active'));
  const target = document.querySelector(`.nav-item[data-view="${button.dataset.view}"]`);
  if (target) target.classList.add('active');
  notify(`${button.textContent.trim().replace(/\s+/g, ' ')} selected.`);
}));
document.getElementById('monitorBtn').addEventListener('click', () => notify('Live monitoring stream connected — 148 sensors online.'));
document.getElementById('mapBtn').addEventListener('click', () => notify('Interactive sector map is ready to explore.'));
document.getElementById('exportBtn').addEventListener('click', () => {
  const report = 'DEEPSEA GUARDIAN — DAILY OCEAN INTELLIGENCE REPORT\n\nWater quality index: 82/100\nBiodiversity score: 76/100\nActive threats: 07\nNetwork coverage: 89%\n';
  const link = document.createElement('a');
  link.href = URL.createObjectURL(new Blob([report], {type: 'text/plain'}));
  link.download = 'deepsea-guardian-report.txt';
  link.click();
  URL.revokeObjectURL(link.href);
  notify('Daily intelligence report downloaded.');
});
