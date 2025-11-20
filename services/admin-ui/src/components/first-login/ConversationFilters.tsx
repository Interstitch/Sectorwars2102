import React from 'react';
import { ConversationFilters as Filters } from '../../types/firstLogin';

interface ConversationFiltersProps {
  filters: Filters;
  onFilterChange: (filters: Filters) => void;
  onRefresh: () => void;
  loading?: boolean;
}

export const ConversationFilters: React.FC<ConversationFiltersProps> = ({
  filters,
  onFilterChange,
  onRefresh,
  loading = false
}) => {
  const handleOutcomeChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    onFilterChange({
      ...filters,
      outcome: e.target.value || undefined,
      skip: 0 // Reset to first page when filter changes
    });
  };

  const handleProviderChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    onFilterChange({
      ...filters,
      ai_provider: e.target.value || undefined,
      skip: 0
    });
  };

  const handleStartDateChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    onFilterChange({
      ...filters,
      start_date: e.target.value || undefined,
      skip: 0
    });
  };

  const handleEndDateChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    onFilterChange({
      ...filters,
      end_date: e.target.value || undefined,
      skip: 0
    });
  };

  const handleClearFilters = () => {
    onFilterChange({
      limit: filters.limit,
      skip: 0
    });
  };

  const hasActiveFilters = !!(filters.outcome || filters.ai_provider || filters.start_date || filters.end_date);

  return (
    <div className="conversation-filters">
      <div className="filter-row">
        <div className="filter-group">
          <label htmlFor="outcome-filter">Outcome</label>
          <select
            id="outcome-filter"
            value={filters.outcome || ''}
            onChange={handleOutcomeChange}
            className="filter-select"
          >
            <option value="">All Outcomes</option>
            <option value="SUCCESS">Success</option>
            <option value="CAUGHT">Caught</option>
            <option value="SUSPICIOUS">Suspicious</option>
            <option value="ABANDONED">Abandoned</option>
          </select>
        </div>

        <div className="filter-group">
          <label htmlFor="provider-filter">AI Provider</label>
          <select
            id="provider-filter"
            value={filters.ai_provider || ''}
            onChange={handleProviderChange}
            className="filter-select"
          >
            <option value="">All Providers</option>
            <option value="anthropic">Anthropic</option>
            <option value="openai">OpenAI</option>
            <option value="fallback">Fallback</option>
          </select>
        </div>

        <div className="filter-group">
          <label htmlFor="start-date-filter">Start Date</label>
          <input
            id="start-date-filter"
            type="date"
            value={filters.start_date || ''}
            onChange={handleStartDateChange}
            className="filter-input"
          />
        </div>

        <div className="filter-group">
          <label htmlFor="end-date-filter">End Date</label>
          <input
            id="end-date-filter"
            type="date"
            value={filters.end_date || ''}
            onChange={handleEndDateChange}
            className="filter-input"
          />
        </div>
      </div>

      <div className="filter-actions">
        {hasActiveFilters && (
          <button
            className="btn btn-secondary"
            onClick={handleClearFilters}
            type="button"
          >
            <i className="fas fa-times"></i>
            Clear Filters
          </button>
        )}
        <button
          className="btn btn-primary"
          onClick={onRefresh}
          disabled={loading}
          type="button"
        >
          <i className={`fas fa-sync ${loading ? 'fa-spin' : ''}`}></i>
          Refresh
        </button>
      </div>
    </div>
  );
};
