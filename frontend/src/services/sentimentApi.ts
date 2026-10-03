import type { SentimentRequest, SentimentResponse } from '@/types/sentiment';
import { API_BASE } from './config';
export async function analyzeSentiment(text: string): Promise<SentimentResponse> {
  const response = await fetch(`${API_BASE}/sentiment/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text } as SentimentRequest),
  });
  if (!response.ok) {
    throw new Error(`Sentiment analysis failed: ${response.status}`);
  }
  return response.json() as Promise<SentimentResponse>;
}
