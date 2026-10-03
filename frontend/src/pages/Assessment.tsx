import React, { useState, useCallback } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import QuestionsLoader from './QuestionsLoader';
import QuestionCard from '@/components/QuestionCard';
import ProgressBar from '@/components/ProgressBar';
import LoadingScreen from '@/components/LoadingScreen';
import type { Question, AssessmentPayload } from '@/types/assessment';
import { predictMentalHealth } from '@/services/mentalHealthApi';

const Assessment: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const state = location.state as { name: string; dob: string; age: number; occupation: string } | null | undefined;
  const [questions, setQuestions] = useState<Question[]>([]);
  const [responses, setResponses] = useState<Record<string, number>>({});
  const [currentPage, setCurrentPage] = useState(0);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const questionsPerPage = 2;
  const loadingQuestions = questions.length === 0 && !!state?.occupation;
  const handleQuestionsLoaded = useCallback((q: Question[]) => {
    setQuestions(q);
  }, []);
  if (loadingQuestions) {
    const occ = (state as { occupation?: string } | null | undefined)?.occupation || '';
    return <QuestionsLoader occupation={occ} onQuestionsLoaded={handleQuestionsLoaded} />;
  }
  if (!state) {
    return (
      <div className="text-center py-16">
        <p className="text-slate-500">Please start the assessment from the beginning.</p>
        <button
          onClick={() => navigate('/wellbeing-intro')}
          className="mt-4 px-6 py-2 bg-primary-600 text-white rounded-lg"
        >
          Start Over
        </button>
      </div>
    );
  }
  const totalPages = Math.ceil(questions.length / questionsPerPage);
  const currentQuestions = questions.slice(
    currentPage * questionsPerPage,
    (currentPage + 1) * questionsPerPage
  );
  const requiredOnPage = currentQuestions.map((q) => q.id);
  const allAnswered = requiredOnPage.every((id) => responses[id] !== undefined);
  const setResponse = (id: string, value: number) => {
    setResponses((prev) => ({ ...prev, [id]: value }));
    setErrors((prev) => ({ ...prev, [id]: '' }));
  };
  const goNext = () => {
    if (!allAnswered) {
      const missing: Record<string, string> = {};
      requiredOnPage.forEach((id) => {
        if (responses[id] === undefined) missing[id] = 'Please answer this question';
      });
      setErrors(missing);
      return;
    }
    if (currentPage < totalPages - 1) {
      setCurrentPage(currentPage + 1);
      setErrors({});
    } else {
      handleSubmit();
    }
  };
  const goPrev = () => {
    if (currentPage > 0) {
      setCurrentPage(currentPage - 1);
      setErrors({});
    }
  };
  const handleSubmit = async () => {
    setLoading(true);
    setSubmitError(null);
    try {
      const payload: AssessmentPayload = {
        name: state.name,
        dateOfBirth: state.dob,
        age: state.age,
        occupation: state.occupation,
        responses,
      };
      const result = await predictMentalHealth(payload);
      navigate('/wellbeing-result', {
        state: {
          result,
          userProfile: {
            name: state.name,
            dateOfBirth: state.dob,
            age: state.age,
            occupation: state.occupation,
          },
        },
      });
    } catch (e) {
      setSubmitError('We couldn\'t process your assessment right now. Please try again.');
    } finally {
      setLoading(false);
    }
  };
  return (
    <div className="animate-fade-in max-w-3xl mx-auto px-4 py-8">
      <div className="mb-6">
        <div className="flex items-center justify-between mb-3">
          <h1 className="text-2xl sm:text-3xl font-bold text-slate-900">Wellbeing Assessment</h1>
          <span className="text-sm text-slate-500">
            Questions {currentPage * questionsPerPage + 1}–{Math.min((currentPage + 1) * questionsPerPage, questions.length)} of {questions.length}
          </span>
        </div>
        <ProgressBar current={currentPage + 1} total={totalPages} />
      </div>
      {submitError && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-4 mb-6 flex items-center gap-3">
          <svg className="w-5 h-5 text-red-500 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
          <div>
            <p className="text-red-700 font-medium">{submitError}</p>
            <button
              onClick={handleSubmit}
              className="text-red-600 font-semibold text-sm mt-1 hover:underline"
            >
              Try Again
            </button>
          </div>
        </div>
      )}
      {loading && <LoadingScreen />}
      {!loading && currentQuestions.map((question) => (
        <QuestionCard
          key={question.id}
          question={question}
          value={responses[question.id] || 0}
          onChange={(val) => setResponse(question.id, val)}
          error={errors[question.id]}
        />
      ))}
      <div className="flex justify-between mt-8">
        <button
          onClick={goPrev}
          disabled={currentPage === 0}
          className={`px-6 py-3 rounded-xl font-semibold transition-colors ${
            currentPage === 0
              ? 'bg-slate-100 text-slate-400 cursor-not-allowed'
              : 'border border-slate-300 text-slate-700 hover:bg-slate-50'
          }`}
        >
          ← Previous
        </button>
        <button
          onClick={goNext}
          disabled={!allAnswered || loading}
          className={`px-8 py-3 rounded-xl font-semibold transition-colors ${
            !allAnswered || loading
              ? 'bg-slate-300 text-slate-500 cursor-not-allowed'
              : currentPage === totalPages - 1
                ? 'bg-sage-600 text-white hover:bg-sage-700'
                : 'bg-primary-600 text-white hover:bg-primary-700'
          }`}
        >
          {currentPage === totalPages - 1 ? 'Complete Assessment' : 'Next →'}
          {!allAnswered && !loading && <span className="ml-2 text-xs">(answer all)</span>}
        </button>
      </div>
    </div>
  );
};
export default Assessment;