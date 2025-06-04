import { useState, useEffect } from 'react';

export const useResource = <T,>(url: string | undefined): LoadState<T> => {
  const [state, setState] = useState<LoadState<T>>({ state: 'Pending' });

  useEffect(() => {
    const fetchData = async () => {
      if (!url) {
        setState({ state: 'Pending' });
        return;
      }
      setState({ state: 'Loading' });
      try {
        const response = await fetch(url);
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        setState({ state: 'Loaded', data });
      } catch (error) {
        console.error('Error loading resource:', error);
        setState({ state: 'Error', error });
      }
    };

    fetchData();
  }, [url]);

  return state;
};export type LoadState<T> = {
  state: 'Pending'
} | {
  state: 'Loading'
} | {
  state: 'Loaded'
  data: T
} | {
  state: 'Error'
  error: any
}

