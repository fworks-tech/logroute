import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { TourTooltip } from './TourTooltip';
import type { TooltipRenderProps } from 'react-joyride';

function makeProps(overrides: Partial<TooltipRenderProps> = {}): TooltipRenderProps {
  const btnProps = {
    'aria-label': '',
    'data-action': '',
    onClick: () => {},
    role: 'button',
    title: '',
  };

  return {
    continuous: true,
    index: 0,
    isLastStep: false,
    size: 5,
    step: {
      target: 'body',
      title: 'Step Title',
      content: 'Step content description.',
      placement: 'bottom',
    } as any,
    backProps: { ...btnProps, 'aria-label': 'Back' },
    closeProps: { ...btnProps, 'aria-label': 'Close' },
    primaryProps: { ...btnProps, 'aria-label': 'Next' },
    skipProps: { ...btnProps, 'aria-label': 'Skip' },
    tooltipProps: { 'aria-modal': true as const, role: 'dialog' as const },
    controls: {
      close: () => {},
      go: () => {},
      info: () => ({ index: 0, lifecycle: 'init', status: 'running', action: 'init', controlled: false, size: 5, origin: null, scrolling: false, waiting: false }),
      next: () => {},
      open: () => {},
      prev: () => {},
      replay: () => {},
      reset: () => {},
      skip: () => {},
      start: () => {},
      stop: () => {},
    },
    ...overrides,
  } as any;
}

describe('TourTooltip', () => {
  it('renders the step title', () => {
    render(<TourTooltip {...makeProps()} />);
    expect(screen.getByText('Step Title')).toBeInTheDocument();
  });

  it('renders the step content', () => {
    render(<TourTooltip {...makeProps()} />);
    expect(screen.getByText('Step content description.')).toBeInTheDocument();
  });

  it('shows progress (1 of 5)', () => {
    render(<TourTooltip {...makeProps()} />);
    expect(screen.getByText('1 of 5')).toBeInTheDocument();
  });

  it('shows progress (3 of 5) for middle step', () => {
    render(<TourTooltip {...makeProps({ index: 2 })} />);
    expect(screen.getByText('3 of 5')).toBeInTheDocument();
  });

  it('renders Next button on non-last steps', () => {
    render(<TourTooltip {...makeProps({ index: 0, size: 5 })} />);
    expect(screen.getByText('Next')).toBeInTheDocument();
  });

  it('renders Done button on the last step', () => {
    render(<TourTooltip {...makeProps({ index: 4, size: 5 })} />);
    expect(screen.getByText('Done')).toBeInTheDocument();
  });

  it('renders Back button when not on the first step', () => {
    render(<TourTooltip {...makeProps({ index: 2 })} />);
    expect(screen.getByText('Back')).toBeInTheDocument();
  });

  it('does not render Back button on the first step', () => {
    render(<TourTooltip {...makeProps({ index: 0 })} />);
    expect(screen.queryByText('Back')).not.toBeInTheDocument();
  });

  it('renders Skip tour and Close buttons', () => {
    render(<TourTooltip {...makeProps()} />);
    expect(screen.getByText('Skip tour')).toBeInTheDocument();
    expect(screen.getByText('Close')).toBeInTheDocument();
  });

  it('renders without a title gracefully', () => {
    const props = makeProps();
    props.step.title = undefined;
    render(<TourTooltip {...props} />);
    expect(screen.getByText('Step content description.')).toBeInTheDocument();
  });
});
