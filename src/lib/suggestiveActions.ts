export interface SuggestiveAction {
  id: string;
  label: string;
  message: string;
}

export const defaultActions: SuggestiveAction[] = [
  { id: 'brief', label: 'Morning supply brief', message: 'Give me the morning supply brief' },
  { id: 'alerts', label: 'Critical alerts', message: 'Show me all critical supply chain alerts' },
  { id: 'inventory', label: 'Inventory risk', message: 'Which SKUs are at risk of stockout?' },
  { id: 'kpis', label: 'KPI dashboard', message: 'Show me the current KPI dashboard overview' },
  { id: 'scenario', label: 'Titanium disruption', message: 'What if titanium supply is disrupted for 3 months?' },
  { id: 'deck', label: 'Generate S&OP deck', message: 'Generate the weekly S&OP presentation' },
  { id: 'forecast', label: 'Demand forecast', message: 'Analyze the demand forecast for landing gear assemblies' },
];
