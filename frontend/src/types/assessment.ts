export interface Question {
  id: string;
  category: string;
  question: string;
  type: 'rating' | 'multiple_choice' | 'number';
  minValue?: number;
  maxValue?: number;
  step?: number;
  options?: string[];
  description?: string;
  unit?: string;
  column?: string;
}
export interface UserProfile {
  name: string;
  dateOfBirth: string;
  age: number;
  occupation: string;
}
export interface AssessmentPayload {
  name: string;
  dateOfBirth: string;
  age: number;
  occupation: string;
  responses: Record<string, number>;
}
export interface AssessmentResponse {
  score: number;
  category: string;
  strengths: string[];
  areas_to_improve: AreaToImprove[];
  notes: string[];
  category_breakdown?: Record<string, number>;
}
export interface AreaToImprove {
  category: string;
  current: string;
  recommendation: string;
  action: string;
}
export interface WellResultData {
  score: number;
  category: string;
  strengths: string[];
  areas_to_improve: AreaToImprove[];
  notes: string[];
  userProfile: UserProfile;
  assessmentDate: string;
}
export interface SentimentRequest {
  text: string;
}
export interface SentimentResponse {
  sentiment: 'Positive' | 'Neutral' | 'Negative';
  score: number;
  emotions?: EmotionResult[];
}
export interface EmotionResult {
  label: string;
  score: number;
}
export interface ApiError {
  message: string;
  code?: string;
}
