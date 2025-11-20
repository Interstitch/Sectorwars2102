/**
 * TypeScript interfaces for First Login conversation data
 * Matches backend API response models from admin_first_login.py
 */

export interface DialogueExchangeDetail {
  id: string;
  sequence_number: number;
  npc_prompt: string;
  player_response: string;
  timestamp: string;
  topic: string | null;

  // Analysis metrics
  persuasiveness: number | null;
  confidence: number | null;
  consistency: number | null;
  believability: number | null;
  current_suspicion: number | null;
  detected_contradictions: string[] | null;

  // AI metadata
  ai_provider: string | null;
  response_time_ms: number | null;
  estimated_cost_usd: number | null;
  tokens_used: number | null;
}

export interface ConversationSummary {
  session_id: string;
  player_username: string;
  player_id: string;
  started_at: string;
  completed_at: string | null;
  ship_claimed: string | null;
  awarded_ship: string | null;
  outcome: string | null;
  final_persuasion_score: number | null;
  negotiation_skill: string | null;
  total_questions: number;
  ai_providers_used: string[];
  total_cost_usd: number;
}

export interface GuardPersonality {
  name: string;
  title: string;
  trait: string;
  description: string;
  base_suspicion: number;
}

export interface ConversationDetail {
  session: ConversationSummary;
  exchanges: DialogueExchangeDetail[];
  guard_personality: GuardPersonality;
}

export interface ConversationStats {
  total_sessions: number;
  completed_sessions: number;
  success_rate: number;
  average_questions: number;
  total_cost_usd: number;
  ai_provider_breakdown: Record<string, number>;
  outcome_breakdown: Record<string, number>;
}

// Filter options for conversation list
export interface ConversationFilters {
  outcome?: string;
  ai_provider?: string;
  start_date?: string;
  end_date?: string;
  skip?: number;
  limit?: number;
}
