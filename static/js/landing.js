// Resume Builder Pro — Landing Page Hero Effects

document.addEventListener('DOMContentLoaded', function () {

  // === 3D Card Parallax Tilt on Mouse Move ===
  const card3D = document.getElementById('resumeCard3D');
  const cardInner = document.getElementById('resumeCard3DInner');
  const badgeATS = document.getElementById('badgeATS');
  const badgePro = document.getElementById('badgePro');

  if (card3D && cardInner) {
    const container = card3D;

    container.addEventListener('mousemove', function (e) {
      const rect = container.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      const centerX = rect.width / 2;
      const centerY = rect.height / 2;
      const rotateX = ((y - centerY) / centerY) * -8;
      const rotateY = ((x - centerX) / centerX) * 10;

      cardInner.style.transform =
        'rotateY(' + rotateY + 'deg) rotateX(' + rotateX + 'deg)';

      // Badges move at different speeds for depth
      if (badgeATS) {
        const atsX = ((x - centerX) / centerX) * 6;
        const atsY = ((y - centerY) / centerY) * -4;
        badgeATS.style.transform =
          'translate(' + atsX + 'px, ' + atsY + 'px) translateZ(40px)';
      }
      if (badgePro) {
        const proX = ((x - centerX) / centerX) * 12;
        const proY = ((y - centerY) / centerY) * -8;
        badgePro.style.transform =
          'translate(' + proX + 'px, ' + proY + 'px)';
      }
    });

    container.addEventListener('mouseleave', function () {
      cardInner.style.transform = '';
      if (badgeATS) badgeATS.style.transform = '';
      if (badgePro) badgePro.style.transform = '';
    });
  }
});
