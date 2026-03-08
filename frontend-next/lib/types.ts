export interface AnzscoAssessment {
  id?: string;
  eligible: boolean;
  occupation: string;
  anzsco_code: string;
  confidence_score: number;
  reason: string;
  assessed_at?: string;
}

export interface Job {
  id: string;
  session_id: string;
  platform: string;
  job_title: string;
  employer_name: string;
  location: string;
  job_description: string;
  salary?: string;
  posted_date: string;
  url: string;
  search_title: string;
  search_location: string;
  scraped_at: string;
  created_at: string;
  anzsco_assessment?: AnzscoAssessment;
}

export interface ScrapeSession {
  id: string;
  platform: string;
  job_titles: string[];
  location: string;
  max_pages: number;
  status: string;
  total_jobs: number;
  eligible_jobs: number;
  error_message?: string;
  started_at: string;
  completed_at?: string;
  created_at: string;
  jobs?: Job[];
}

export interface Company {
  id: string;
  name: string;
  description: string;
  website: string;
  industry: string;
  source: string;
  source_url: string;
  anzsco_eligible: boolean;
  job_count: number;
  hubspot_id?: string;
  hubspot_status: string;
  hubspot_synced_at?: string;
  created_at: string;
  updated_at: string;
}

export interface DashboardStats {
  total_sessions: number;
  total_jobs: number;
  eligible_jobs: number;
  total_companies: number;
  platforms: { platform: string; count: number }[];
}

export type Platform = "indeed" | "seek" | "careerone";
