//! C2SP tlog-tiles paths and layout, ported from Part 09 (`09_tiles.py`).

pub const HEIGHT: u32 = 8;
pub const WIDTH: u64 = 1 << HEIGHT; // 256 hashes per full tile

/// Which kind of file a tile path names.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Kind {
    /// Hashes at tile level L (0 to 63).
    Level(u8),
    /// An entry bundle, beside level 0 tile N.
    Entries,
}

/// The index N in groups of three digits; every group but the last starts with "x".
pub fn n_path(mut n: u64) -> String {
    let mut groups = vec![];
    loop {
        groups.push(n % 1000);
        n /= 1000;
        if n == 0 {
            break;
        }
    }
    groups.reverse();
    let last = groups.len() - 1;
    groups
        .iter()
        .enumerate()
        .map(|(i, g)| if i < last { format!("x{g:03}") } else { format!("{g:03}") })
        .collect::<Vec<_>>()
        .join("/")
}

fn suffix(width: u64) -> String {
    if width == WIDTH { String::new() } else { format!(".p/{width}") }
}

pub fn tile_path(level: u8, index: u64, width: u64) -> String {
    assert!(level <= 63 && (1..=WIDTH).contains(&width));
    format!("tile/{level}/{}{}", n_path(index), suffix(width))
}

pub fn entries_path(index: u64, width: u64) -> String {
    assert!((1..=WIDTH).contains(&width));
    format!("tile/entries/{}{}", n_path(index), suffix(width))
}

fn decimal_no_leading_zero(s: &str) -> Option<u64> {
    if s.is_empty() || !s.bytes().all(|c| c.is_ascii_digit()) || (s.len() > 1 && s.starts_with('0')) {
        return None;
    }
    s.parse().ok()
}

/// Parses a tile path strictly: any spelling the spec forbids is an error, so one tile has one name.
pub fn parse_tile_path(p: &str) -> Result<(Kind, u64, u64), String> {
    let bad = || format!("bad tile path: {p}");
    let parts: Vec<&str> = p.split('/').collect();
    if parts.len() < 3 || parts[0] != "tile" {
        return Err(bad());
    }
    let kind = if parts[1] == "entries" {
        Kind::Entries
    } else {
        match decimal_no_leading_zero(parts[1]) {
            Some(l) if l <= 63 => Kind::Level(l as u8),
            _ => return Err(bad()),
        }
    };
    let mut rest: Vec<&str> = parts[2..].to_vec();
    let mut width = WIDTH;
    if rest.len() >= 2 && rest[rest.len() - 2].ends_with(".p") {
        width = match decimal_no_leading_zero(rest[rest.len() - 1]) {
            Some(w) if (1..=255).contains(&w) => w,
            _ => return Err(bad()),
        };
        let n = rest.len();
        let stem = &rest[n - 2][..rest[n - 2].len() - 2];
        rest.truncate(n - 2);
        rest.push(stem);
    }
    let (last, dirs) = rest.split_last().ok_or_else(bad)?;
    let mut index: u64 = 0;
    for (i, d) in dirs.iter().enumerate() {
        let ok = d.len() == 4 && d.starts_with('x') && d[1..].bytes().all(|c| c.is_ascii_digit());
        if !ok || (i == 0 && &d[1..] == "000") {
            return Err(bad());
        }
        index = index.checked_mul(1000).and_then(|v| v.checked_add(d[1..].parse().ok()?)).ok_or_else(bad)?;
    }
    if last.len() != 3 || !last.bytes().all(|c| c.is_ascii_digit()) {
        return Err(bad());
    }
    index = index.checked_mul(1000).and_then(|v| v.checked_add(last.parse().ok()?)).ok_or_else(bad)?;
    Ok((kind, index, width))
}

/// Every tile of a tree of `size` entries: (level, index, width), level by level.
pub fn layout(size: u64) -> Vec<(u8, u64, u64)> {
    let mut out = vec![];
    let mut level: u32 = 0;
    while level * HEIGHT < 64 && (size >> (HEIGHT * level)) != 0 {
        let row = size >> (HEIGHT * level);
        for i in 0..row / WIDTH {
            out.push((level as u8, i, WIDTH));
        }
        if !row.is_multiple_of(WIDTH) {
            out.push((level as u8, row / WIDTH, row % WIDTH));
        }
        level += 1;
    }
    out
}

/// A tree node (level, index) lives in tile (tile level, tile index), at (node level, node index) inside it.
pub fn node_to_tile(level: u32, index: u64) -> (u32, u64, u32, u64) {
    let (tl, r) = (level / HEIGHT, level % HEIGHT);
    let pos = index << r;
    (tl, pos / WIDTH, r, (pos % WIDTH) >> r)
}
