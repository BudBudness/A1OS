const programs = [
  'Orphan Support',
  'Widow & Vulnerable Family Support',
  'Youth Empowerment',
  'Health & Awareness Achievements',
  'Blood Donation Drives',
  'Mental Health Awareness',
  'Refugee Outreach',
  'Orphanage Partnerships',
  'Women/Girls in Tech',
  'Environmental Awareness',
];

const events = [
  'Stramos Run For Hope',
  'Stramos LifeShare Blood Drive',
  'Stramos Mind & Hope Conference',
  'Stramos Future Builders Summit',
  'Stramos Refugee Hope Outreach',
  'Stramos Women in Tech Summit',
  'Stramos Green Future Initiative',
];

const contacts = ['+256700709940', '+256783409327', '+256759902139'];

export default function Home() {
  return (
    <main className="min-h-screen bg-[#0A0A0A] text-white">
      <section className="mx-auto flex max-w-7xl flex-col gap-12 px-6 py-10 md:px-10 lg:px-16">
        <nav className="flex items-center justify-between border-b border-white/10 pb-5">
          <div>
            <p className="text-sm uppercase tracking-[0.45em] text-[#D62828]">Love Wins</p>
            <h1 className="text-xl font-black tracking-tight">STRAMOS WISDOM CHARITY</h1>
          </div>
          <a className="rounded-full bg-[#D62828] px-5 py-3 text-sm font-bold" href="#contact">Contact</a>
        </nav>

        <div className="grid gap-10 lg:grid-cols-[1.1fr_0.9fr] lg:items-center">
          <div className="space-y-8">
            <div className="inline-flex rounded-full border border-white/15 px-4 py-2 text-sm text-white/80">James 1:27 in Action</div>
            <div className="space-y-5">
              <h2 className="max-w-4xl text-5xl font-black uppercase leading-none md:text-7xl">
                Compassion. Community. Action.
              </h2>
              <p className="max-w-2xl text-lg leading-8 text-white/75">
                Inclusive humanitarian infrastructure supporting orphans, widows, vulnerable youth,
                refugees, and underserved communities through outreach, health awareness, empowerment,
                environmental action, women/girls in tech, and strategic partnerships.
              </p>
            </div>
            <div className="flex flex-wrap gap-3">
              <a href="#programs" className="rounded-full bg-white px-6 py-3 font-bold text-black">Explore Programs</a>
              <a href="#volunteer" className="rounded-full border border-white/20 px-6 py-3 font-bold">Volunteer</a>
            </div>
          </div>

          <div className="rounded-[2rem] border border-white/10 bg-white/[0.03] p-6 shadow-2xl">
            <div className="rounded-[1.5rem] border border-white/10 bg-black p-8 text-center">
              <div className="mx-auto mb-6 grid h-40 w-40 place-items-center rounded-full border-4 border-white shadow-2xl">
                <div className="text-7xl font-black">R</div>
              </div>
              <p className="text-sm uppercase tracking-[0.4em] text-[#D62828]">Brand Mark</p>
              <h3 className="mt-3 text-3xl font-black">STRAMOS</h3>
              <h3 className="text-3xl font-black tracking-[0.2em]">WISDOM</h3>
              <p className="mt-2 text-xl font-black tracking-[0.45em] text-[#D62828]">CHARITY</p>
            </div>
          </div>
        </div>
      </section>

      <section id="programs" className="bg-white px-6 py-16 text-black md:px-10 lg:px-16">
        <div className="mx-auto max-w-7xl">
          <p className="text-sm font-bold uppercase tracking-[0.35em] text-[#D62828]">Programs</p>
          <h2 className="mt-3 text-4xl font-black uppercase">Humanitarian Operating System</h2>
          <div className="mt-10 grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {programs.map((program) => (
              <div key={program} className="rounded-3xl border border-black/10 p-6">
                <div className="mb-5 h-2 w-12 rounded-full bg-[#D62828]" />
                <h3 className="text-xl font-black">{program}</h3>
                <p className="mt-3 text-sm leading-6 text-black/65">
                  Structured outreach, documentation, partnerships, volunteer coordination, and measurable impact.
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="px-6 py-16 md:px-10 lg:px-16">
        <div className="mx-auto max-w-7xl">
          <p className="text-sm font-bold uppercase tracking-[0.35em] text-[#D62828]">Events</p>
          <h2 className="mt-3 text-4xl font-black uppercase">Flagship Initiatives</h2>
          <div className="mt-10 grid gap-4 md:grid-cols-2">
            {events.map((event) => (
              <div key={event} className="flex items-center justify-between rounded-3xl border border-white/10 bg-white/[0.03] p-6">
                <h3 className="text-xl font-black">{event}</h3>
                <span className="text-[#D62828]">●</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section id="volunteer" className="bg-[#D62828] px-6 py-16 text-white md:px-10 lg:px-16">
        <div className="mx-auto grid max-w-7xl gap-8 md:grid-cols-2 md:items-center">
          <div>
            <p className="text-sm font-bold uppercase tracking-[0.35em] text-white/80">Join the Movement</p>
            <h2 className="mt-3 text-4xl font-black uppercase">Volunteer. Partner. Support.</h2>
          </div>
          <p className="text-lg leading-8 text-white/90">
            We welcome individuals, schools, churches, businesses, hospitals, NGOs, and community leaders who want to serve with dignity and visible action.
          </p>
        </div>
      </section>

      <section id="contact" className="px-6 py-16 md:px-10 lg:px-16">
        <div className="mx-auto max-w-7xl rounded-[2rem] border border-white/10 bg-white/[0.03] p-8">
          <p className="text-sm font-bold uppercase tracking-[0.35em] text-[#D62828]">Contact</p>
          <h2 className="mt-3 text-4xl font-black uppercase">Official Channels</h2>
          <div className="mt-8 grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            {contacts.map((phone) => (
              <a key={phone} href={`tel:${phone}`} className="rounded-2xl border border-white/10 p-5 font-bold">{phone}</a>
            ))}
            <a href="mailto:igahussein4@gmail.com" className="rounded-2xl border border-white/10 p-5 font-bold">igahussein4@gmail.com</a>
          </div>
          <p className="mt-8 text-white/60">TikTok: @stramoswisdomcharity</p>
        </div>
      </section>
    </main>
  );
}
