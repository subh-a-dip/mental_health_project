import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';

const occupations = [
  'Student',
  'Working Professional',
  'Self-Employed',
  'Homemaker',
  'Retired',
  'Unemployed',
  'Other',
];

const UserInformation: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const state = location.state as { dob: string; occupation: string; age: number } | null;
  const [name, setName] = useState('');
  const [occupation, setOccupation] = useState(state?.occupation || '');
  const [age, setAge] = useState(state?.age || 0);
  const dob = state?.dob || '';
  const [errors, setErrors] = useState<Record<string, string>>({});

  const handleSubmit = () => {
    const newErrors: Record<string, string> = {};
    if (!name.trim()) newErrors.name = 'Please enter your full name';
    if (!occupation) newErrors.occupation = 'Please select your occupation';
    if (!age || age <= 0) newErrors.age = 'Please enter a valid age';
    setErrors(newErrors);
    if (Object.keys(newErrors).length === 0) {
      navigate('/assessment', {
        state: { name, dob, age, occupation },
      });
    }
  };

  return (
    <div className="animate-fade-in max-w-2xl mx-auto px-4 py-12">
      <div className="text-center mb-8">
        <h1 className="text-3xl sm:text-4xl font-bold text-slate-900 mb-4">Your Profile</h1>
        <p className="text-slate-600">Tell us a bit about yourself.</p>
      </div>
      <div className="bg-white rounded-2xl p-6 sm:p-8 border border-slate-200 shadow-sm space-y-5">
        <div className="p-4 bg-slate-50 rounded-xl text-sm text-slate-600 flex items-center gap-2">
          <svg className="w-4 h-4 text-primary-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
          Your responses are used to generate your assessment. Avoid entering highly sensitive personal information.
        </div>
        <div>
          <label htmlFor="name" className="block text-sm font-semibold text-slate-700 mb-2">
            Full Name
          </label>
          <input
            id="name"
            type="text"
            value={name}
            onChange={(e) => { setName(e.target.value); setErrors((p) => ({ ...p, name: '' })); }}
            placeholder="Enter your full name"
            className={`w-full px-4 py-3 rounded-xl border ${errors.name ? 'border-red-300' : 'border-slate-300'} focus:ring-2 focus:ring-primary-500 focus:outline-none`}
            aria-describedby="name-error"
          />
          {errors.name && <p id="name-error" className="text-red-500 text-sm mt-1">{errors.name}</p>}
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
          <label htmlFor="age" className="block text-sm font-semibold text-slate-700 mb-2">
            Age
          </label>
          <input
            id="age"
            type="number"
            min="1"
            max="120"
            value={age || ''}
            onChange={(e) => { setAge(parseInt(e.target.value) || 0); setErrors((p) => ({ ...p, age: '' })); }}
            className={`w-full px-4 py-3 rounded-xl border ${errors.age ? 'border-red-300' : 'border-slate-300'} focus:ring-2 focus:ring-primary-500 focus:outline-none`}
            aria-describedby="age-error"
          />
          {errors.age && <p id="age-error" className="text-red-500 text-sm mt-1">{errors.age}</p>}
        </div>
          <div>
          <label htmlFor="dob2" className="block text-sm font-semibold text-slate-700 mb-2">
            Date of Birth
          </label>
          <input
            id="dob2"
            type="date"
            value={dob}
            readOnly
            className="w-full px-4 py-3 rounded-xl border border-slate-200 bg-slate-50 text-slate-500"
            aria-label="Date of birth (from previous step)"
          />
        </div>
        </div>
        <div>
          <label htmlFor="occupation2" className="block text-sm font-semibold text-slate-700 mb-2">
            Occupation
          </label>
          <select
            id="occupation2"
            value={occupation}
            onChange={(e) => { setOccupation(e.target.value); setErrors((p) => ({ ...p, occupation: '' })); }}
            className={`w-full px-4 py-3 rounded-xl border ${errors.occupation ? 'border-red-300' : 'border-slate-300'} focus:ring-2 focus:ring-primary-500 focus:outline-none`}
            aria-describedby="occupation-error"
          >
            <option value="">Select occupation...</option>
            {occupations.map((occ) => (
              <option key={occ} value={occ}>{occ}</option>
            ))}
          </select>
          {errors.occupation && <p id="occupation-error" className="text-red-500 text-sm mt-1">{errors.occupation}</p>}
        </div>
        <div className="bg-slate-50 rounded-xl p-4 text-sm text-slate-600">
          <h4 className="font-semibold text-slate-800 mb-2">Preview</h4>
          <p><strong>Name:</strong> {name || '—'}</p>
          <p><strong>Age:</strong> {age || '—'}</p>
          <p><strong>Occupation:</strong> {occupation || '—'}</p>
        </div>
        <div className="flex justify-between">
          <button
            onClick={() => navigate('/wellbeing-intro')}
            className="px-6 py-3 border border-slate-300 text-slate-700 font-semibold rounded-xl hover:bg-slate-50 transition-colors"
          >
            ← Back
          </button>
          <button
            onClick={handleSubmit}
            className="px-8 py-3 bg-primary-600 text-white font-semibold rounded-xl hover:bg-primary-700 transition-colors focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2"
          >
            Continue →
          </button>
        </div>
      </div>
    </div>
  );
};

export default UserInformation;