import React from "react";

const programmes = [
  {
    title: "Playgroup & Early Years",
    age: "18 months – 3 years",
    text: "A gentle beginning built around practical life, movement, language, sensory exploration, routines and secure relationships.",
  },
  {
    title: "Montessori Nursery",
    age: "3 – 5 years",
    text: "Children learn through purposeful hands-on activity, choice, repetition and carefully prepared learning environments.",
  },
  {
    title: "Kindergarten",
    age: "5 – 6 years",
    text: "A stronger academic foundation through literacy, numeracy, cultural exploration, creativity, independence and school readiness.",
  },
  {
    title: "Full-Day Daycare",
    age: "Early years",
    text: "A nurturing full-day environment combining care, routines, play, rest and meaningful early learning."
  }
];

const learningAreas = [
  "Practical Life",
  "Sensorial Exploration",
  "Language & Early Literacy",
  "Mathematics & Numeracy",
  "Culture, Nature & Discovery",
  "Creative Arts",
  "Movement & Outdoor Play",
  "Social & Emotional Development"
];

export function App() {
  return (
    <div className="site">
      <header className="nav">
        <div className="container nav-inner">
          <a className="brand" href="#home" aria-label="Little Oaks home">
            <span className="brand-mark">LO</span>
            <span>
              <strong>Little Oaks</strong>
              <small>Montessori Nursery & Kindergarten</small>
            </span>
          </a>

          <nav>
            <a href="#programmes">Programmes</a>
            <a href="#learning">Learning</a>
            <a href="#about">About</a>
            <a href="#contact">Contact</a>
          </nav>

          <a className="nav-cta" href="#contact">Enquire</a>
        </div>
      </header>

      <main id="home">
        <section className="hero">
          <div className="container hero-grid">
            <div className="hero-copy">
              <p className="eyebrow">NURTURE · EXPLORE · GROW</p>
              <h1>
                A beautiful beginning
                <span>for little minds.</span>
              </h1>
              <p className="hero-text">
                Little Oaks Montessori Kindergarten & Day Care Centre is an
                early childhood environment where children are cared for,
                encouraged to explore and supported as they grow in
                independence, confidence and love of learning.
              </p>

              <div className="actions">
                <a className="button primary" href="#contact">Talk to Little Oaks</a>
                <a className="button secondary" href="#programmes">Explore programmes</a>
              </div>

              <div className="hero-facts">
                <div>
                  <strong>18 mo – 6 yrs</strong>
                  <span>Early childhood</span>
                </div>
                <div>
                  <strong>Montessori-inspired</strong>
                  <span>Hands-on learning</span>
                </div>
                <div>
                  <strong>Mbarara</strong>
                  <span>Nyamitanga</span>
                </div>
              </div>
            </div>

            <div className="hero-card">
              <div className="sun"></div>
              <div className="tree tree-one"></div>
              <div className="tree tree-two"></div>
              <div className="card-content">
                <span className="card-label">THE LITTLE OAKS WAY</span>
                <h2>Small hands.<br />Big discoveries.</h2>
                <p>
                  Children learn by doing — touching, moving, choosing,
                  repeating, asking questions and discovering the world around
                  them.
                </p>
                <div className="leaf-row">
                  <span>Explore</span>
                  <span>Discover</span>
                  <span>Grow</span>
                </div>
              </div>
            </div>
          </div>
        </section>

        <section className="intro" id="about">
          <div className="container intro-grid">
            <div>
              <p className="eyebrow">WELCOME TO LITTLE OAKS</p>
              <h2>More than childcare.<br />A foundation for life.</h2>
            </div>
            <div className="intro-copy">
              <p>
                The early years are when children develop the foundations for
                how they think, communicate, relate to others and approach new
                experiences.
              </p>
              <p>
                Little Oaks combines nurturing care with Montessori-inspired
                early learning so children can develop at their own pace while
                building independence, concentration, confidence and practical
                skills.
              </p>
            </div>
          </div>
        </section>

        <section className="programmes" id="programmes">
          <div className="container">
            <div className="section-heading">
              <div>
                <p className="eyebrow">OUR PROGRAMMES</p>
                <h2>A place to belong,<br />learn and grow.</h2>
              </div>
              <p>
                Programmes designed around the developmental needs of young
                children — from their first experiences away from home through
                to kindergarten and school readiness.
              </p>
            </div>

            <div className="programme-grid">
              {programmes.map((programme) => (
                <article className="programme-card" key={programme.title}>
                  <span className="programme-age">{programme.age}</span>
                  <h3>{programme.title}</h3>
                  <p>{programme.text}</p>
                  <span className="arrow">→</span>
                </article>
              ))}
            </div>
          </div>
        </section>

        <section className="learning" id="learning">
          <div className="container learning-grid">
            <div className="learning-panel">
              <p className="eyebrow">THE MONTESSORI APPROACH</p>
              <h2>Learning begins with curiosity.</h2>
              <p>
                A prepared environment gives children meaningful opportunities
                to work with their hands, make choices, practise skills and
                develop concentration. The adult guides the child rather than
                doing everything for them.
              </p>
              <p>
                At Little Oaks, this philosophy can become part of everyday
                learning — from practical routines and sensory discovery to
                language, mathematics, creativity and understanding the world.
              </p>
            </div>

            <div className="areas">
              {learningAreas.map((area, index) => (
                <div className="area" key={area}>
                  <span>{String(index + 1).padStart(2, "0")}</span>
                  <strong>{area}</strong>
                </div>
              ))}
            </div>
          </div>
        </section>

        <section className="promise">
          <div className="container promise-inner">
            <p className="eyebrow">OUR PROMISE</p>
            <h2>Every child deserves to be known.</h2>
            <p>
              We believe children flourish when they feel safe, respected,
              understood and trusted to try. Our goal is not simply to prepare
              children for the next classroom, but to help them become capable,
              curious and confident young people.
            </p>
          </div>
        </section>

        <section className="contact" id="contact">
          <div className="container contact-grid">
            <div>
              <p className="eyebrow">COME AND MEET US</p>
              <h2>Let's start your child's<br />Little Oaks journey.</h2>
              <p>
                Parents and guardians are welcome to contact Little Oaks to
                discuss programmes, availability, visits and enrolment.
              </p>
            </div>

            <div className="contact-card">
              <div>
                <span>LOCATION</span>
                <strong>Nyamitanga, Mbarara</strong>
                <p>Along Isingiro Road, Uganda</p>
              </div>

              <div>
                <span>CALL / WHATSAPP</span>
                <a href="tel:+256762023393">+256 762 023393</a>
                <a href="tel:+256705074279">+256 705 074279</a>
              </div>

              <div>
                <span>EMAIL</span>
                <a href="mailto:admin@littleoaksmontessori.ac.ug">
                  admin@littleoaksmontessori.ac.ug
                </a>
              </div>

              <a
                className="button primary full"
                href="https://wa.me/256762023393"
                target="_blank"
                rel="noreferrer"
              >
                Message Little Oaks on WhatsApp
              </a>
            </div>
          </div>
        </section>
      </main>

      <footer>
        <div className="container footer-inner">
          <div>
            <strong>Little Oaks Montessori Kindergarten & Day Care Centre (U) Limited</strong>
            <span>Nyamitanga, Mbarara · Uganda</span>
          </div>
          <div>
            <span>URSB Registration: 80034303611084</span>
            <span>© {new Date().getFullYear()} Little Oaks</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
