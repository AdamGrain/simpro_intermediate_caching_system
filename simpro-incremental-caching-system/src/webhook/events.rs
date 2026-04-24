use super::variants::{Operation, Resource};
use std::sync::{LazyLock, Mutex, MutexGuard};
use std::{array, mem};
use strum::{EnumCount, IntoEnumIterator};

/// Number of `(Resource, Operation)` pairs.
const BUFFER_LENGTH: usize =
    Resource::COUNT * Operation::COUNT;

/// Array of record ID arrays indexed by row-major flattening:
/// ```ignore
/// index = (resource as usize) * Operation::COUNT + (operation as usize)`
/// ```
pub type Buffer = [Vec<u64>; BUFFER_LENGTH];

#[derive(Debug)]
/// Thread-safe buffer of `BUFFER_LENGTH` containing `Vec<u32>`
/// values of IDs of records pending retrieval.
pub struct EventBuffer {
    inner: Mutex<Buffer>,
}

impl Default for EventBuffer {
    /// Creates an empty buffer with one IDs array
    /// per (`Resource`, `Operation`) combination.
    ///
    /// Allocation size is fixed based on `BUFFER_LENGTH`.
    fn default() -> Self {
        Self {
            inner: Mutex::new(array::from_fn(|_| {
                Vec::new()
            })),
        }
    }
}

impl EventBuffer {
    /// Acquires exclusive access to the buffer.
    /// Recovers poisoned locks by returning the inner value.
    pub fn acquire_lock(&self) -> MutexGuard<'_, Buffer> {
        self.inner.lock().unwrap_or_else(|e| e.into_inner())
    }

    /// Computes the index of a
    /// (`Resource`, `Operation`) pair.
    #[inline]
    pub fn index(
        resource: Resource,
        operation: Operation,
    ) -> usize {
        resource as usize * Operation::COUNT
            + operation as usize
    }

    /// Returns a (`Resource`, `Operation`) pair
    /// for an index.
    pub fn reverse_index(
        index: usize,
    ) -> (Resource, Operation) {
        RESOURCE_OPERATION[index]
    }

    /// Atomically drains the entire buffer, returning the IDs of records pending retrieval.
    /// for each (`Resource`, `Operation`).
    /// * Overwrites internal `[Vec<u64>; BUFFER_LENGTH]` with empty vectors via `mem::take`.
    /// * Requires exclusive mutex access over the entire buffer.
    pub fn drain(&self) -> Buffer {
        mem::take(&mut *self.acquire_lock())
    }
}

/// Lazily constructed index mapping derived from
/// compiler iteration over enum variants
/// in sequential order
static RESOURCE_OPERATION: LazyLock<
    Vec<(Resource, Operation)>,
> = LazyLock::new(|| {
    Resource::iter()
        .flat_map(|r| {
            Operation::iter().map(move |o| (r, o))
        })
        .collect()
});
