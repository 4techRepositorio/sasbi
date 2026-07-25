const { describe, it } = require('node:test');
const assert = require('node:assert/strict');
const { login, publishDataset } = require('./api-client');

describe('api-client contracts', () => {
  it('exports login and publish helpers', () => {
    assert.equal(typeof login, 'function');
    assert.equal(typeof publishDataset, 'function');
  });
});
