'use client';

import { useState } from 'react';
import dynamic from 'next/dynamic';

// This is the key change: Load the chart component dynamically
const DynamicChart = dynamic(() => import('./components/DynamicChart'), {
  ssr: false, // This ensures the component only renders on the client side
  loading: () => <p>Loading chart...</p> // Optional: Show a loading message
});

// Define the structure of our API response
interface ApiResponse {
  data: any[];
  chartType: string;
  insight: string;
  sqlQuery: string;
  error?: string;
  raw_output?: string;
}

export default function Home() {
  const [question, setQuestion] = useState('');
  const [response, setResponse] = useState<ApiResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!question.trim()) return;

    setIsLoading(true);
    setResponse(null);
    setError('');

    try {
      const res = await fetch('http://localhost:8000/api/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question }),
      });

      const data: ApiResponse = await res.json();

      if (data.error) {
        setError(`${data.error} (Check console for raw output if available)`);
        console.error("Raw output from backend:", data.raw_output);
      } else {
        setResponse(data);
      }

    } catch (err: any) {
      setError(err.message || 'An unexpected error occurred.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <main className="flex min-h-screen flex-col items-center p-4 sm:p-12 md:p-24 bg-gray-50 font-sans">
      <div className="w-full max-w-4xl">
        <h1 className="text-4xl font-bold text-gray-800 text-center mb-2">📊 Northwind AI Analyst</h1>
        <p className="text-center text-gray-500 mb-8">Ask a question about the database to generate a chart and insights.</p>

        <form onSubmit={handleSubmit} className="flex gap-2">
          <input
            type="text"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="e.g., Top 5 employees by sales revenue"
            className="flex-grow p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none"
            disabled={isLoading}
          />
          <button
            type="submit"
            className="bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-700 disabled:bg-blue-300"
            disabled={isLoading}
          >
            {isLoading ? 'Thinking...' : 'Ask'}
          </button>
        </form>

        <div className="mt-8">
          {isLoading && <p className="text-center text-gray-500">Generating response...</p>}
          {error && <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded-lg" role="alert">{error}</div>}

          {response && (
            <div className="bg-white p-6 rounded-xl shadow-md border border-gray-200 animate-fade-in">
              <p className="text-lg text-gray-700 mb-4 border-l-4 border-blue-500 pl-4">
                <strong>Insight:</strong> {response.insight}
              </p>

              <div className="w-full h-80 md:h-96 my-4">
                <DynamicChart
                  chartType={response.chartType}
                  data={response.data}
                />
              </div>

              <details className="mt-4">
                <summary className="cursor-pointer text-sm font-medium text-gray-600 hover:text-gray-900">
                  Show Generated SQL Query
                </summary>
                <code className="block bg-gray-100 text-gray-800 p-3 mt-2 rounded-md text-sm whitespace-pre-wrap">
                  {response.sqlQuery}
                </code>
              </details>
            </div>
          )}
        </div>
      </div>
    </main>
  );
}