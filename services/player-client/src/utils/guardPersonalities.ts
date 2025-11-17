/**
 * Guard Personality System for First Login
 *
 * Generates randomized guard personalities to make each First Login experience unique.
 * Guards have different names, traits, and base suspicion levels that affect interactions.
 */

export interface GuardPersonality {
  name: string;
  title: string;
  trait: string;
  baseSuspicion: number; // 0.0-1.0
  description: string;
}

const GUARD_FIRST_NAMES = [
  'Chen', 'Rodriguez', 'Sato', 'O\'Brien', 'Kowalski', 'Singh',
  'Müller', 'Nakamura', 'Garcia', 'Petrov', 'Kim', 'Anderson'
];

const GUARD_TITLES = [
  'Security Officer',
  'Guard',
  'Security Chief',
  'Station Inspector',
  'Docking Authority',
  'Customs Officer'
];

const GUARD_TRAITS = [
  {
    name: 'Strict Rule-Follower',
    baseSuspicion: 0.6,
    description: 'By-the-book enforcer who trusts procedure over instinct'
  },
  {
    name: 'Friendly Veteran',
    baseSuspicion: 0.3,
    description: 'Experienced officer who\'s seen it all and can spot a good story'
  },
  {
    name: 'Paranoid Newbie',
    baseSuspicion: 0.7,
    description: 'Fresh recruit trying to prove themselves, suspicious of everyone'
  },
  {
    name: 'Tired Night-Shifter',
    baseSuspicion: 0.4,
    description: 'Exhausted from long shifts, just wants to process paperwork quickly'
  },
  {
    name: 'Shrewd Investigator',
    baseSuspicion: 0.5,
    description: 'Keen observer who listens carefully and catches inconsistencies'
  },
  {
    name: 'Cynical Bureaucrat',
    baseSuspicion: 0.55,
    description: 'Seen too many lies to trust anyone easily'
  }
];

/**
 * Generate a random guard personality
 */
export function generateGuardPersonality(): GuardPersonality {
  const firstName = GUARD_FIRST_NAMES[Math.floor(Math.random() * GUARD_FIRST_NAMES.length)];
  const title = GUARD_TITLES[Math.floor(Math.random() * GUARD_TITLES.length)];
  const trait = GUARD_TRAITS[Math.floor(Math.random() * GUARD_TRAITS.length)];

  return {
    name: firstName,
    title,
    trait: trait.name,
    baseSuspicion: trait.baseSuspicion,
    description: trait.description
  };
}

/**
 * Get a consistent guard personality for a session
 * Uses session ID as seed for deterministic randomness
 */
export function getGuardForSession(sessionId: string): GuardPersonality {
  // Simple hash function to convert session ID to number
  let hash = 0;
  for (let i = 0; i < sessionId.length; i++) {
    const char = sessionId.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash = hash & hash; // Convert to 32-bit integer
  }

  // Use hash to seed selections
  const nameIndex = Math.abs(hash) % GUARD_FIRST_NAMES.length;
  const titleIndex = Math.abs(hash >> 4) % GUARD_TITLES.length;
  const traitIndex = Math.abs(hash >> 8) % GUARD_TRAITS.length;

  const firstName = GUARD_FIRST_NAMES[nameIndex];
  const title = GUARD_TITLES[titleIndex];
  const trait = GUARD_TRAITS[traitIndex];

  return {
    name: firstName,
    title,
    trait: trait.name,
    baseSuspicion: trait.baseSuspicion,
    description: trait.description
  };
}
