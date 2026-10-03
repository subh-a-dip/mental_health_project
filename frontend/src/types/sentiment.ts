export interface SentimentRequest {
  text: string;
}
export interface SentimentResponse {
  sentiment: 'Positive' | 'Neutral' | 'Negative';
  /** Polarity strength in [0,1]; consistent with the sentiment verdict shown. */
  score: number;
  emotions?: EmotionResult[];
  /** 7-class mental-health model verdict, not the polarity verdict. */
  predicted_class?: string;
  clinical_confidence?: number;
  vader_compound?: number;
  all_probabilities?: Record<string, number>;
}
export interface EmotionResult {
  label: string;
  score: number;
}
export interface SentimentAnalysisResult {
  sentiment: string;
  score: number;
  analyzedText: string;
}
