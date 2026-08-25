const { AeonriftClient, EventType, EventSource, SideEffectType, ReversibilityType } = require('../dist/index.js');
const assert = require('assert');

console.log('🧪 Running AEONRIFT TypeScript SDK Test Suite...');

try {
  // Test 1: Client instantiation
  const client = new AeonriftClient('test-exec-101', './test_storage');
  assert.strictEqual(client.executionId, 'test-exec-101');
  console.log('  ✓ Test 1: Client instantiation succeeded');

  // Test 2: Event creation
  const event = client.createEvent(
    EventType.TOOL_CALL_INITIATED,
    EventSource.RUNTIME_INTERCEPTOR,
    { tool_name: 'test_tool', input: { arg: 1 } }
  );
  assert.strictEqual(event.execution_id, 'test-exec-101');
  assert.ok(event.hash && event.hash.length === 64, 'SHA-256 hash valid');
  console.log('  ✓ Test 2: Event creation & SHA-256 hashing succeeded');

  // Test 3: Side effect recording & idempotency check
  const record = client.registerSideEffect('payment_api', { amount: 100 }, SideEffectType.API_WRITE, ReversibilityType.IRREVERSIBLE);
  assert.strictEqual(record.status, 'COMMITTED');
  assert.ok(record.idempotency_key, 'Idempotency key generated');

  const recheck = client.checkIdempotency(record.idempotency_key);
  assert.strictEqual(recheck, true, 'Idempotency lock verified');
  console.log('  ✓ Test 3: Side-effect ledger idempotency check succeeded');

  // Test 4: Checkpoint hash calculation
  const checkpoint = client.createCheckpoint('L3', { state_var: 'active' });
  assert.strictEqual(checkpoint.level, 'L3');
  assert.ok(checkpoint.state_hash, 'Checkpoint state hash computed');
  console.log('  ✓ Test 4: Layered checkpoint creation succeeded');

  console.log('\n🎉 ALL AEONRIFT TYPESCRIPT SDK TESTS PASSED CLEANLY (4/4)');
} catch (err) {
  console.error('\n❌ SDK TEST FAILED:', err.message);
  process.exit(1);
}
