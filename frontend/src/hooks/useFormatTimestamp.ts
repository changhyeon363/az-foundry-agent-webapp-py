import { useCallback } from 'react';

/**
 * Hook to format timestamps as absolute time.
 * 
 * @returns A memoized formatter function
 * 
 * @example
 * ```tsx
 * function MessageTimestamp({ timestamp }: { timestamp: Date }) {
 *   const formatTimestamp = useFormatTimestamp();
 *   return <span>{formatTimestamp(timestamp)}</span>;
 * }
 * ```
 * 
 * Example: "10:30 AM"
 */
export const useFormatTimestamp = () => {
  return useCallback((date: Date | undefined): string => {
    if (!date) {
      return '';
    }

    // Always show absolute time
    return new Intl.DateTimeFormat('en', {
      hour: 'numeric',
      minute: '2-digit',
      hour12: true,
    }).format(date);
  }, []);
};
