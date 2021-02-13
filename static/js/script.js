window.parseISOString = function parseISOString(s) {
  var b = s.split(/\D+/);
  return new Date(Date.UTC(b[0], --b[1], b[2], b[3], b[4], b[5], b[6]));
};

$(document).ready(function(){
  $('.slider').slick({
      slidesToShow: 3,
      slidesToScroll: 1,
      autoplay: true,
      autoplaySpeed: 3000,
      nextArrow: $('.next'),
      prevArrow: $('.prev'),
      responsive: [
          {
            breakpoint: 1200,
            settings: {
              slidesToShow: 3,
              infinite: true,
              dots: true
            }
          },
          {
            breakpoint: 768,
            settings: {
              slidesToShow: 2,
            }
          },
          {
            breakpoint: 520,
            settings: {
              slidesToShow: 1,
            }
          }
      ]
    });
})

const lines = document.querySelector('.lines');
const navbar = document.querySelector('nav');
const links = document.querySelectorAll('.navbar li');

lines.addEventListener("click", () => {
navbar.classList.toggle("open");
})

// localStorage.setItem('userInfo', JSON.stringify(userInfo));
// document.getElementById('my-pro').addEventListener('click', getMe);

// function getMe(e){
//   e.preventDefault();
//   var token = JSON.parse(localStorage.getItem('userInfo'));
//   console.log('Authorization=Bearer ${token}')
//   fetch
// }

document.getElementById("btn-start").onclick = function () {
  location.href = "/grades";
  };
  



