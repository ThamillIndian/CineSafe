import { useState } from 'react';

export function useAnalysisData() {
  const [data, setData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const loadData = async (result) => {
    setIsLoading(true);
    try {
      setData(result);
      setError(null);
    } catch (err) {
      setError(err.message);
      console.error('Error loading data:', err);
    } finally {
      setIsLoading(false);
    }
  };

  return { data, isLoading, error, loadData };
}
