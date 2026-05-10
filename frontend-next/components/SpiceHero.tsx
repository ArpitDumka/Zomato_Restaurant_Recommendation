"use client";

import Image from "next/image";

const HERO_IMAGE =
  "https://images.unsplash.com/photo-1504674900247-0877df9cc836?auto=format&fit=crop&w=1600&q=80";

export default function SpiceHero() {
  return (
    <section className="hero" id="discover">
      <div className="hero-media">
        <Image
          src={HERO_IMAGE}
          alt=""
          fill
          className="hero-bg-image"
          sizes="(max-width: 1260px) 100vw, 1260px"
          priority
        />
      </div>
      <div className="hero-ribbon" title="Educational UI inspired by food-discovery apps">
        INSPIRED UI · DEMO
      </div>
      <div className="hero-content">
        <h1>Your Next Favorite Meal, Instantly</h1>
        <p className="lead">
          Discover top dining picks tailored to your taste, with smart AI reasons, trusted
          ratings, and budget clarity — one vivid board at a time.
        </p>
      </div>
    </section>
  );
}
