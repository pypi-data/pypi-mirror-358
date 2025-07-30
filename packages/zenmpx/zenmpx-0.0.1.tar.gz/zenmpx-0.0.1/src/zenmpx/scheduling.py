def bin_packing_first_fit(hardware_event_groups, bin_size, decreasing=True):
    """
    Use First Fit algorithm to schedule hardware event groups into bins.

    Args:
        hardware_event_groups: list of lists, each sublist represents a group of hardware events
        bin_size: int, capacity of each bin

    Returns:
        list of lists of lists, representing the packed bins
    """
    # initialize items with their sizes
    items_with_size = [(group, len(group)) for group in hardware_event_groups]

    # sort items by size (First Fit)
    items_with_size.sort(key=lambda x: x[1], reverse=decreasing)
    # if decreasing is True, sort in descending order; otherwise, sort in ascending order

    # initialize bins and their sizes
    bins = []
    bin_sizes = []  # record the current size of each bin

    # iterate over each item and place it in the first bin that can accommodate it
    for item, item_size in items_with_size:
        # try to place the item in an existing bin
        placed = False
        for i in range(len(bins)):
            if bin_sizes[i] + item_size <= bin_size:
                bins[i].append(item)
                bin_sizes[i] += item_size
                placed = True
                break

        # if the item could not be placed in any existing bin, create a new bin
        if not placed:
            bins.append([item])
            bin_sizes.append(item_size)

    return bins


def bin_packing_best_fit(hardware_event_groups, bin_size, decreasing=True):
    """
    Use Best Fit algorithm to schedule hardware event groups into bins.

    Args:
        hardware_event_groups: list of lists, each sublist represents a group of hardware events
        bin_size: int, capacity of each bin

    Returns:
        list of lists of lists, representing the packed bins
    """
    # initialize items with their sizes
    items_with_size = [(group, len(group)) for group in hardware_event_groups]

    # sort items by size (Best Fit)
    items_with_size.sort(key=lambda x: x[1], reverse=decreasing)

    # initialize bins and their sizes
    bins = []
    bin_sizes = []  # record the current size of each bin

    # iterate over each item and place it in the best bin that can accommodate it
    for item, item_size in items_with_size:
        best_bin_index = -1
        min_space_left = float("inf")

        # find the best bin for the item
        for i in range(len(bins)):
            space_left = bin_size - bin_sizes[i]
            if space_left >= item_size and space_left < min_space_left:
                min_space_left = space_left
                best_bin_index = i

        # if a suitable bin was found, place the item there
        if best_bin_index != -1:
            bins[best_bin_index].append(item)
            bin_sizes[best_bin_index] += item_size
        else:
            # if no suitable bin was found, create a new bin
            bins.append([item])
            bin_sizes.append(item_size)

    return bins


def bin_packing_optimal_dp(hardware_event_groups, bin_size):
    """
    Use dynamic programming with state compression to find optimal bin packing.

    Args:
        hardware_event_groups: list of lists, each sublist represents a group of hardware events
        bin_size: int, capacity of each bin

    Returns:
        list of lists of lists, representing the packed bins
    """
    n = len(hardware_event_groups)
    sizes = [len(group) for group in hardware_event_groups]

    # Precompute all valid subsets that can fit in one bin
    valid_subsets = []
    for mask in range(1, 1 << n):
        total_size = sum(sizes[i] for i in range(n) if mask & (1 << i))
        if total_size <= bin_size:
            valid_subsets.append(mask)

    # DP: dp[mask] = minimum number of bins to pack items in mask
    dp = [float("inf")] * (1 << n)
    parent = [-1] * (1 << n)
    dp[0] = 0

    for mask in range(1 << n):
        if dp[mask] == float("inf"):
            continue

        # Try all valid subsets for the next bin
        for subset in valid_subsets:
            # Check if this subset doesn't overlap with already packed items
            if mask & subset == 0:
                new_mask = mask | subset
                if dp[new_mask] > dp[mask] + 1:
                    dp[new_mask] = dp[mask] + 1
                    parent[new_mask] = subset

    # Reconstruct solution
    bins = []
    current_mask = (1 << n) - 1

    while current_mask > 0:
        subset = parent[current_mask]
        bin_items = []
        for i in range(n):
            if subset & (1 << i):
                bin_items.append(hardware_event_groups[i])
        bins.append(bin_items)
        current_mask ^= subset

    return bins
