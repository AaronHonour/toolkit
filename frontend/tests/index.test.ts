import { version } from '../src/index';

describe('Toolkit Frontend', () => {
  it('should export version', () => {
    expect(version).toBeDefined();
    expect(typeof version).toBe('string');
  });
});
