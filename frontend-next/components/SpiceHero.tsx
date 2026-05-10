type Props = { appVersion: string };

export default function SpiceHero({ appVersion }: Props) {
  return (
    <section className="hero card" id="discover">
      <div className="hero-content">
        <h1>Your Next Favorite Meal, Instantly</h1>
        <p className="lead">
          Discover top dining picks tailored to your taste, with smart AI reasons, trusted
          ratings, and budget clarity in one sleek view.
        </p>
        <p className="hero-meta">
          App <code>{appVersion}</code> · Next.js + Railway API
        </p>
      </div>
    </section>
  );
}
