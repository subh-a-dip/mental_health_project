import React, { useEffect, useState } from 'react';
import { getQuestions } from '@/services/mentalHealthApi';
import LoadingScreen from '@/components/LoadingScreen';
import type { Question } from '@/types/assessment';

interface Props {
  onQuestionsLoaded: (questions: Question[]) => void;
  occupation: string;
}

const QuestionsLoader: React.FC<Props> = ({ onQuestionsLoaded, occupation }) => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    const load = async () => {
      try {
        const questions = await getQuestions(occupation);
        if (!cancelled) {
          onQuestionsLoaded(questions);
          setLoading(false);
        }
      } catch (e) {
        if (!cancelled) {
          setError('Could not load questions. Please try again.');
          setLoading(false);
        }
      }
    };
    load();
    return () => { cancelled = true; };
  }, [occupation, onQuestionsLoaded]);

  if (loading) return <LoadingScreen message="Loading questions..." subMessage="Preparing personalized questions for you." />;
  if (error) return <div className="text-center py-16 text-red-500">{error}</div>;
  return null;
};

export default QuestionsLoader;