import io.jenetics.*;
import io.jenetics.engine.*;
import io.jenetics.util.*;

import javax.swing.*;
import java.awt.*;
import java.awt.geom.*;
import java.util.*;
import java.util.List;
import java.util.stream.*;
import com.google.gson.*;
import com.google.gson.reflect.TypeToken;
import java.io.*;
import java.nio.file.Files;
import java.nio.file.Paths;

// ============================================================================
// Domain Classes with Multiple Shapes
// ============================================================================

enum ShapeType {
    RECTANGLE, TRIANGLE, CIRCLE
}

class Dimensions {
    double width, height;
    ShapeType shapeType;

    public Dimensions(double width, double height, ShapeType shapeType) {
        this.width = width;
        this.height = height;
        this.shapeType = shapeType;
    }

    public double getArea() {
        switch (shapeType) {
            case RECTANGLE:
                return width * height;
            case TRIANGLE:
                return (width * height) / 2.0;
            case CIRCLE:
                return Math.PI * Math.pow(Math.min(width, height) / 2.0, 2);
            default:
                return width * height;
        }
    }

    public List<Dimensions> getAllOrientations() {
        List<Dimensions> orientations = new ArrayList<>();
        orientations.add(new Dimensions(width, height, shapeType));

        // For rectangles and triangles, add rotated version
        if ((shapeType == ShapeType.RECTANGLE || shapeType == ShapeType.TRIANGLE) && width != height) {
            orientations.add(new Dimensions(height, width, shapeType));
        }

        // Circles don't need rotation
        return orientations;
    }

    public Rectangle2D getBoundingBox(Position pos) {
        return new Rectangle2D.Double(pos.x, pos.y, width, height);
    }
}

class Position {
    double x, y;

    public Position(double x, double y) {
        this.x = x;
        this.y = y;
    }

    @Override
    public String toString() {
        return String.format("(%.1f, %.1f)", x, y);
    }
}

class Item {
    int id;
    String type;
    Dimensions originalDimensions;
    double pricePerUnit;

    public Item(int id, String type, Dimensions dimensions, double pricePerUnit) {
        this.id = id;
        this.type = type;
        this.originalDimensions = dimensions;
        this.pricePerUnit = pricePerUnit;
    }
}

class Bin {
    int id;
    Dimensions dimensions;
    List<PlacedItem> placedItems;

    public Bin(int id, Dimensions dimensions) {
        this.id = id;
        this.dimensions = dimensions;
        this.placedItems = new ArrayList<>();
    }

    public Bin copy() {
        return new Bin(this.id, this.dimensions);
    }

    public double getUsedArea() {
        return placedItems.stream()
                .mapToDouble(pi -> pi.dimensions.getArea())
                .sum();
    }

    public double getUtilization() {
        if (dimensions.getArea() == 0) return 0;
        return getUsedArea() / dimensions.getArea();
    }

    public Optional<Position> findBestFitPosition(Dimensions itemDimensions) {
        List<Position> potentialPositions = new ArrayList<>();
        potentialPositions.add(new Position(0, 0));

        for (PlacedItem existingItem : placedItems) {
            potentialPositions.add(new Position(existingItem.position.x + existingItem.dimensions.width, existingItem.position.y));
            potentialPositions.add(new Position(existingItem.position.x, existingItem.position.y + existingItem.dimensions.height));
        }

        Position bestPosition = null;

        for (Position pos : potentialPositions) {
            PlacedItem candidate = new PlacedItem(null, pos, itemDimensions);

            if (candidate.fitsInBin(this) && !isOverlapping(candidate)) {
                if (bestPosition == null || (pos.y < bestPosition.y) || (pos.y == bestPosition.y && pos.x < bestPosition.x)) {
                    bestPosition = pos;
                }
            }
        }
        return Optional.ofNullable(bestPosition);
    }

    private boolean isOverlapping(PlacedItem newItem) {
        for (PlacedItem existingItem : placedItems) {
            if (newItem.overlaps(existingItem)) {
                return true;
            }
        }
        return false;
    }
}

class PlacedItem {
    Item item;
    Position position;
    Dimensions dimensions;

    public PlacedItem(Item item, Position position, Dimensions dimensions) {
        this.item = item;
        this.position = position;
        this.dimensions = dimensions;
    }

    public boolean overlaps(PlacedItem other) {
        Rectangle2D thisBounds = dimensions.getBoundingBox(position);
        Rectangle2D otherBounds = other.dimensions.getBoundingBox(other.position);
        return thisBounds.intersects(otherBounds);
    }

    public boolean fitsInBin(Bin bin) {
        return position.x >= 0 && position.y >= 0 &&
                position.x + dimensions.width <= bin.dimensions.width &&
                position.y + dimensions.height <= bin.dimensions.height;
    }
}

class PackingResult {
    List<Bin> bins;
    List<Item> unplacedItems;
    double totalPackedValue;
    double totalWastedValue;

    public PackingResult(List<Bin> bins, List<Item> allItems) {
        this.bins = bins;
        this.unplacedItems = new ArrayList<>();
        Set<Integer> placedItemIds = bins.stream()
                .flatMap(b -> b.placedItems.stream())
                .map(pi -> pi.item.id)
                .collect(Collectors.toSet());

        for (Item item : allItems) {
            if (!placedItemIds.contains(item.id)) {
                this.unplacedItems.add(item);
            }
        }
        this.totalPackedValue = allItems.stream()
                .filter(item -> placedItemIds.contains(item.id))
                .mapToDouble(item -> item.pricePerUnit)
                .sum();
        this.totalWastedValue = this.unplacedItems.stream()
                .mapToDouble(item -> item.pricePerUnit)
                .sum();
    }
}

// ============================================================================
// JSON Data Classes
// ============================================================================

class JsonItem {
    int id;
    String type;
    double width;
    double height;
    String shape;
    double price;
    
    public JsonItem() {}
    
    public JsonItem(int id, String type, double width, double height, String shape, double price) {
        this.id = id;
        this.type = type;
        this.width = width;
        this.height = height;
        this.shape = shape;
        this.price = price;
    }
}

class JsonBin {
    int id;
    double width;
    double height;
    
    public JsonBin() {}
    
    public JsonBin(int id, double width, double height) {
        this.id = id;
        this.width = width;
        this.height = height;
    }
}

class JsonInput {
    List<JsonItem> items;
    List<JsonBin> bins;
    
    public JsonInput() {}
    
    public JsonInput(List<JsonItem> items, List<JsonBin> bins) {
        this.items = items;
        this.bins = bins;
    }
}

class JsonPlanStep {
    int step;
    int item_id;
    String item_type;
    int bin_id;
    double x;
    double y;
    double width;
    double height;
    String shape;
    
    public JsonPlanStep() {}
    
    public JsonPlanStep(int step, int item_id, String item_type, int bin_id, 
                       double x, double y, double width, double height, String shape) {
        this.step = step;
        this.item_id = item_id;
        this.item_type = item_type;
        this.bin_id = bin_id;
        this.x = x;
        this.y = y;
        this.width = width;
        this.height = height;
        this.shape = shape;
    }
}

class JsonBinResult {
    int bin_id;
    double utilization;
    int items_count;
    
    public JsonBinResult() {}
    
    public JsonBinResult(int bin_id, double utilization, int items_count) {
        this.bin_id = bin_id;
        this.utilization = utilization;
        this.items_count = items_count;
    }
}

class JsonOutput {
    double fitness;
    double packed_value;
    int unplaced_items;
    List<JsonPlanStep> plan;
    List<JsonBinResult> bins;
    
    public JsonOutput() {}
    
    public JsonOutput(double fitness, double packed_value, int unplaced_items, 
                     List<JsonPlanStep> plan, List<JsonBinResult> bins) {
        this.fitness = fitness;
        this.packed_value = packed_value;
        this.unplaced_items = unplaced_items;
        this.plan = plan;
        this.bins = bins;
    }
}

// ============================================================================
// JSON Utility Classes
// ============================================================================

class JsonOutputGenerator {
    private static final Gson gson = new GsonBuilder().setPrettyPrinting().create();
    
    public static String generateJsonOutput(PackingResult result, double fitness) {
        List<JsonPlanStep> plan = new ArrayList<>();
        int step = 1;
        
        for (Bin bin : result.bins) {
            for (PlacedItem pi : bin.placedItems) {
                plan.add(new JsonPlanStep(
                    step++,
                    pi.item.id,
                    pi.item.type,
                    bin.id,
                    pi.position.x,
                    pi.position.y,
                    pi.dimensions.width,
                    pi.dimensions.height,
                    pi.dimensions.shapeType.name()
                ));
            }
        }
        
        List<JsonBinResult> binResults = result.bins.stream()
            .map(bin -> new JsonBinResult(
                bin.id,
                bin.getUtilization() * 100,
                bin.placedItems.size()
            ))
            .collect(Collectors.toList());
        
        JsonOutput output = new JsonOutput(
            fitness,
            result.totalPackedValue,
            result.unplacedItems.size(),
            plan,
            binResults
        );
        
        return gson.toJson(output);
    }
}

class CommandLineParser {
    private String inputFile;
    private boolean headless = false;
    
    public boolean parse(String[] args) {
        for (int i = 0; i < args.length; i++) {
            if (args[i].equals("--input") && i + 1 < args.length) {
                inputFile = args[i + 1];
                i++; // Skip next argument
            } else if (args[i].equals("--headless")) {
                headless = true;
            }
        }
        return inputFile != null;
    }
    
    public String getInputFile() { return inputFile; }
    public boolean isHeadless() { return headless; }
}

class JsonInputLoader {
    private static final Gson gson = new Gson();
    
    public static JsonInput loadFromFile(String filename) throws IOException {
        String content = new String(Files.readAllBytes(Paths.get(filename)));
        return gson.fromJson(content, JsonInput.class);
    }
    
    public static List<Item> convertToItems(List<JsonItem> jsonItems) {
        List<Item> items = new ArrayList<>();
        for (JsonItem jsonItem : jsonItems) {
            ShapeType shapeType = ShapeType.valueOf(jsonItem.shape);
            Dimensions dimensions = new Dimensions(jsonItem.width, jsonItem.height, shapeType);
            items.add(new Item(jsonItem.id, jsonItem.type, dimensions, jsonItem.price));
        }
        return items;
    }
    
    public static List<Bin> convertToBins(List<JsonBin> jsonBins) {
        List<Bin> bins = new ArrayList<>();
        for (JsonBin jsonBin : jsonBins) {
            Dimensions dimensions = new Dimensions(jsonBin.width, jsonBin.height, ShapeType.RECTANGLE);
            bins.add(new Bin(jsonBin.id, dimensions));
        }
        return bins;
    }
}

// ============================================================================
// Genetic Algorithm Components
// ============================================================================

class SolutionDecoder {
    private final List<Item> items;
    private final List<Bin> originalBins;
    private final Map<Integer, List<Dimensions>> itemOrientations;

    public SolutionDecoder(List<Item> items, List<Bin> bins) {
        this.items = items;
        this.originalBins = bins;
        this.itemOrientations = items.stream()
                .collect(Collectors.toMap(
                        item -> item.id,
                        item -> item.originalDimensions.getAllOrientations()
                ));
    }

    public PackingResult decode(Genotype<IntegerGene> genotype) {
        List<Bin> freshBins = originalBins.stream().map(Bin::copy).collect(Collectors.toList());

        final IntegerChromosome orderChromosome = (IntegerChromosome) genotype.get(0);
        final IntegerChromosome binAssignmentChromosome = (IntegerChromosome) genotype.get(1);
        final IntegerChromosome rotationChromosome = (IntegerChromosome) genotype.get(2);

        List<Integer> itemIndices = IntStream.range(0, items.size()).boxed()
                .sorted(Comparator.comparingInt(i -> orderChromosome.get(i).allele()))
                .collect(Collectors.toList());

        for (int itemIndex : itemIndices) {
            Item item = items.get(itemIndex);
            int binId = binAssignmentChromosome.get(itemIndex).allele();
            int rotationIndex = rotationChromosome.get(itemIndex).allele();

            Bin targetBin = freshBins.get(binId);
            List<Dimensions> orientations = itemOrientations.get(item.id);
            Dimensions rotatedDimensions = orientations.get(rotationIndex % orientations.size());

            Optional<Position> maybePosition = targetBin.findBestFitPosition(rotatedDimensions);

            if (maybePosition.isPresent()) {
                PlacedItem placedItem = new PlacedItem(item, maybePosition.get(), rotatedDimensions);
                targetBin.placedItems.add(placedItem);
            }
        }
        return new PackingResult(freshBins, items);
    }
}

// ============================================================================
// Visualization Components
// ============================================================================

class BinPanel extends JPanel {
    private Bin bin;
    private final Map<String, Color> colorMap;
    private static final int SCALE = 2;
    private static final int PADDING = 10;

    public BinPanel(Map<String, Color> colorMap) {
        this.colorMap = colorMap;
        setBackground(Color.WHITE);
        setBorder(BorderFactory.createLineBorder(Color.DARK_GRAY, 2));
    }

    public void setBin(Bin bin) {
        this.bin = bin;
        repaint();
    }

    @Override
    protected void paintComponent(Graphics g) {
        super.paintComponent(g);
        if (bin == null) return;

        Graphics2D g2d = (Graphics2D) g;
        g2d.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);

        int binWidth = (int) (bin.dimensions.width * SCALE);
        int binHeight = (int) (bin.dimensions.height * SCALE);

        // Draw bin boundary
        g2d.setColor(new Color(240, 240, 240));
        g2d.fillRect(PADDING, PADDING, binWidth, binHeight);
        g2d.setColor(Color.DARK_GRAY);
        g2d.setStroke(new BasicStroke(2));
        g2d.drawRect(PADDING, PADDING, binWidth, binHeight);

        // Draw placed items with different shapes
        for (PlacedItem pi : bin.placedItems) {
            int x = PADDING + (int) (pi.position.x * SCALE);
            int y = PADDING + (int) (pi.position.y * SCALE);
            int w = (int) (pi.dimensions.width * SCALE);
            int h = (int) (pi.dimensions.height * SCALE);

            Color itemColor = colorMap.getOrDefault(pi.item.type, Color.GRAY);
            g2d.setColor(itemColor);

            switch (pi.dimensions.shapeType) {
                case RECTANGLE:
                    g2d.fillRect(x, y, w, h);
                    g2d.setColor(Color.BLACK);
                    g2d.setStroke(new BasicStroke(1));
                    g2d.drawRect(x, y, w, h);
                    break;

                case TRIANGLE:
                    int[] xPoints = {x, x + w, x + w/2};
                    int[] yPoints = {y + h, y + h, y};
                    g2d.fillPolygon(xPoints, yPoints, 3);
                    g2d.setColor(Color.BLACK);
                    g2d.setStroke(new BasicStroke(1));
                    g2d.drawPolygon(xPoints, yPoints, 3);
                    break;

                case CIRCLE:
                    int diameter = Math.min(w, h);
                    g2d.fillOval(x, y, diameter, diameter);
                    g2d.setColor(Color.BLACK);
                    g2d.setStroke(new BasicStroke(1));
                    g2d.drawOval(x, y, diameter, diameter);
                    break;
            }
        }
    }

    @Override
    public Dimension getPreferredSize() {
        if (bin == null) return new Dimension(300, 300);
        return new Dimension(
                (int) (bin.dimensions.width * SCALE) + 2 * PADDING,
                (int) (bin.dimensions.height * SCALE) + 2 * PADDING
        );
    }
}

class StatisticsPanel extends JPanel {
    private JLabel generationLabel;
    private JLabel fitnessLabel;
    private JLabel avgFitnessLabel;
    private JLabel packedValueLabel;
    private JLabel utilizationLabel;
    private JLabel unplacedItemsLabel;
    private JLabel statusLabel;

    public StatisticsPanel() {
        setLayout(new GridLayout(7, 1, 5, 5));
        setBorder(BorderFactory.createTitledBorder("Statistics"));
        setBackground(Color.WHITE);

        generationLabel = new JLabel("Generation: 0");
        fitnessLabel = new JLabel("Best Fitness: 0.00");
        avgFitnessLabel = new JLabel("Avg Fitness: 0.00");
        packedValueLabel = new JLabel("Packed Value: $0.00");
        utilizationLabel = new JLabel("Avg Utilization: 0.0%");
        unplacedItemsLabel = new JLabel("Unplaced Items: 0");
        statusLabel = new JLabel("Status: Running...");

        Font font = new Font("Monospaced", Font.BOLD, 14);
        generationLabel.setFont(font);
        fitnessLabel.setFont(font);
        avgFitnessLabel.setFont(font);
        packedValueLabel.setFont(font);
        utilizationLabel.setFont(font);
        unplacedItemsLabel.setFont(font);

        Font statusFont = new Font("Arial", Font.BOLD, 16);
        statusLabel.setFont(statusFont);
        statusLabel.setForeground(new Color(0, 100, 0));

        add(generationLabel);
        add(fitnessLabel);
        add(avgFitnessLabel);
        add(packedValueLabel);
        add(utilizationLabel);
        add(unplacedItemsLabel);
        add(statusLabel);
    }

    public void updateStats(int generation, double bestFitness, double avgFitness, PackingResult result) {
        generationLabel.setText(String.format("Generation: %d", generation));
        fitnessLabel.setText(String.format("Best Fitness: %.2f", bestFitness));
        avgFitnessLabel.setText(String.format("Avg Fitness: %.2f", avgFitness));
        packedValueLabel.setText(String.format("Packed Value: $%.2f", result.totalPackedValue));

        double avgUtil = result.bins.stream()
                .filter(b -> !b.placedItems.isEmpty())
                .mapToDouble(Bin::getUtilization)
                .average()
                .orElse(0.0);
        utilizationLabel.setText(String.format("Avg Utilization: %.1f%%", avgUtil * 100));
        unplacedItemsLabel.setText(String.format("Unplaced Items: %d", result.unplacedItems.size()));
    }

    public void setFinished() {
        statusLabel.setText("Status: FINISHED!");
        statusLabel.setForeground(new Color(0, 150, 0));
    }
}

class BinDetailsPanel extends JPanel {
    public BinDetailsPanel() {
        setLayout(new BoxLayout(this, BoxLayout.Y_AXIS));
        setBackground(Color.WHITE);
        setBorder(BorderFactory.createTitledBorder("Bin Details"));
    }

    public void updateDetails(List<Bin> bins) {
        removeAll();

        for (Bin bin : bins) {
            JPanel binInfo = new JPanel();
            binInfo.setLayout(new BoxLayout(binInfo, BoxLayout.Y_AXIS));
            binInfo.setBorder(BorderFactory.createLineBorder(Color.LIGHT_GRAY));
            binInfo.setBackground(Color.WHITE);
            binInfo.setAlignmentX(Component.LEFT_ALIGNMENT);

            JLabel title = new JLabel(String.format("Bin %d (%.0f×%.0f)",
                    bin.id, bin.dimensions.width, bin.dimensions.height));
            title.setFont(new Font("Arial", Font.BOLD, 12));
            binInfo.add(title);

            Map<String, Long> typeCounts = bin.placedItems.stream()
                    .collect(Collectors.groupingBy(pi -> pi.item.type, Collectors.counting()));

            for (Map.Entry<String, Long> entry : typeCounts.entrySet()) {
                JLabel itemLabel = new JLabel(String.format("  %s: %d", entry.getKey(), entry.getValue()));
                itemLabel.setFont(new Font("Arial", Font.PLAIN, 11));
                binInfo.add(itemLabel);
            }

            double usedArea = bin.getUsedArea();
            double freeArea = bin.dimensions.getArea() - usedArea;
            JLabel spaceLabel = new JLabel(String.format("  Used: %.0f | Free: %.0f (%.1f%%)",
                    usedArea, freeArea, bin.getUtilization() * 100));
            spaceLabel.setFont(new Font("Arial", Font.ITALIC, 11));
            binInfo.add(spaceLabel);

            binInfo.add(Box.createVerticalStrut(5));
            add(binInfo);
        }

        revalidate();
        repaint();
    }
}

class VisualizationFrame extends JFrame {
    private final List<BinPanel> binPanels;
    private final StatisticsPanel statsPanel;
    private final BinDetailsPanel detailsPanel;
    private final Map<String, Color> colorMap;

    public VisualizationFrame(List<Bin> bins, List<Item> items) {
        setTitle("2D Bin Packing Genetic Algorithm - Multiple Shapes");
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setLayout(new BorderLayout(10, 10));

        // Create color map for item types
        colorMap = new HashMap<>();
        List<String> types = items.stream().map(i -> i.type).distinct().collect(Collectors.toList());
        Color[] colors = {
                new Color(255, 99, 71),   // Red
                new Color(100, 149, 237), // Blue
                new Color(144, 238, 144), // Green
                new Color(255, 165, 0),   // Orange
                new Color(147, 112, 219), // Purple
                new Color(255, 192, 203), // Pink
                new Color(255, 215, 0),   // Gold
                new Color(64, 224, 208)   // Turquoise
        };
        for (int i = 0; i < types.size(); i++) {
            colorMap.put(types.get(i), colors[i % colors.length]);
        }

        // Top panel for bins
        JPanel binsPanel = new JPanel();
        binsPanel.setBackground(Color.WHITE);
        binsPanel.setLayout(new FlowLayout(FlowLayout.LEFT, 15, 10));

        binPanels = new ArrayList<>();
        for (Bin bin : bins) {
            BinPanel binPanel = new BinPanel(colorMap);
            binPanel.setBin(bin);
            binPanels.add(binPanel);
            binsPanel.add(binPanel);
        }

        JScrollPane binsScrollPane = new JScrollPane(binsPanel);
        binsScrollPane.setPreferredSize(new Dimension(1400, 500));

        // Right panel for statistics and details
        JPanel rightPanel = new JPanel();
        rightPanel.setLayout(new BoxLayout(rightPanel, BoxLayout.Y_AXIS));
        rightPanel.setBackground(Color.WHITE);

        statsPanel = new StatisticsPanel();
        detailsPanel = new BinDetailsPanel();

        rightPanel.add(statsPanel);
        rightPanel.add(detailsPanel);

        JScrollPane rightScrollPane = new JScrollPane(rightPanel);
        rightScrollPane.setPreferredSize(new Dimension(350, 500));

        // Add legend
        JPanel legendPanel = new JPanel(new FlowLayout(FlowLayout.LEFT));
        legendPanel.setBorder(BorderFactory.createTitledBorder("Legend"));
        legendPanel.setBackground(Color.WHITE);
        for (Map.Entry<String, Color> entry : colorMap.entrySet()) {
            JLabel legendItem = new JLabel("■ " + entry.getKey());
            legendItem.setForeground(entry.getValue());
            legendItem.setFont(new Font("Arial", Font.BOLD, 12));
            legendPanel.add(legendItem);
        }

        add(legendPanel, BorderLayout.NORTH);
        add(binsScrollPane, BorderLayout.CENTER);
        add(rightScrollPane, BorderLayout.EAST);

        pack();
        setLocationRelativeTo(null);
    }

    public void updateVisualization(int generation, double bestFitness, double avgFitness, PackingResult result) {
        SwingUtilities.invokeLater(() -> {
            for (int i = 0; i < result.bins.size(); i++) {
                binPanels.get(i).setBin(result.bins.get(i));
            }
            statsPanel.updateStats(generation, bestFitness, avgFitness, result);
            detailsPanel.updateDetails(result.bins);
        });
    }

    public void markFinished() {
        SwingUtilities.invokeLater(() -> {
            statsPanel.setFinished();
        });
    }
}

// ============================================================================
// Bin Packing Problem with Visualization
// ============================================================================

class BinPackingProblem {
    private final List<Item> items;
    private final List<Bin> bins;
    private final SolutionDecoder decoder;
    private VisualizationFrame visualizationFrame;
    private boolean headless;

    public BinPackingProblem(List<Item> items, List<Bin> bins) {
        this.items = items;
        this.bins = bins;
        this.decoder = new SolutionDecoder(items, bins);
        this.headless = false;
    }
    
    public BinPackingProblem(List<Item> items, List<Bin> bins, boolean headless) {
        this.items = items;
        this.bins = bins;
        this.decoder = new SolutionDecoder(items, bins);
        this.headless = headless;
    }

    public Genotype<IntegerGene> createGenotype() {
        int numItems = items.size();
        IntegerChromosome itemOrder = IntegerChromosome.of(0, numItems, numItems);
        IntegerChromosome binAssignment = IntegerChromosome.of(0, bins.size(), numItems);
        IntegerChromosome rotation = IntegerChromosome.of(0, 2, numItems);
        return Genotype.of(itemOrder, binAssignment, rotation);
    }

    public double fitness(Genotype<IntegerGene> genotype) {
        PackingResult result = decoder.decode(genotype);
        double packedValueScore = result.totalPackedValue;
        double avgUtilization = result.bins.stream()
                .filter(b -> !b.placedItems.isEmpty())
                .mapToDouble(Bin::getUtilization)
                .average()
                .orElse(0.0);
        double utilizationBonus = avgUtilization * 100;
        return packedValueScore + utilizationBonus;
    }

    public void solve() {
        if (!headless) {
            // Initialize visualization
            SwingUtilities.invokeLater(() -> {
                visualizationFrame = new VisualizationFrame(bins, items);
                visualizationFrame.setVisible(true);
            });

            // Wait for frame to be visible
            try {
                Thread.sleep(500);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }

        System.out.println("=".repeat(80));
        System.out.println("2D BIN PACKING OPTIMIZATION - MULTIPLE SHAPES & 4 BINS");
        System.out.println("=".repeat(80));

        Engine<IntegerGene, Double> engine = Engine
                .builder(this::fitness, this::createGenotype)
                .populationSize(200)
                .survivorsSelector(new TournamentSelector<>(5))
                .offspringSelector(new RouletteWheelSelector<>())
                .alterers(
                        new UniformCrossover<>(0.4),
                        new SinglePointCrossover<>(0.4),
                        new Mutator<>(0.2)
                )
                .maximizing()
                .build();

        Phenotype<IntegerGene, Double> best = engine.stream()
                .limit(Limits.bySteadyFitness(70))
                .limit(500)
                .peek(er -> {
                    PackingResult result = decoder.decode(er.bestPhenotype().genotype());

                    // Calculate average fitness of population
                    double avgFitness = er.population().stream()
                            .mapToDouble(Phenotype::fitness)
                            .average()
                            .orElse(0.0);

                    if (!headless) {
                        visualizationFrame.updateVisualization(
                                (int) er.generation(),
                                er.bestFitness(),
                                avgFitness,
                                result
                        );
                    }

                    if (er.generation() % 10 == 0) {
                        System.out.printf("Generation %3d: Best Fitness = %.2f | Avg Fitness = %.2f%n",
                                er.generation(), er.bestFitness(), avgFitness);
                    }

                    if (!headless) {
                        try {
                            Thread.sleep(50);
                        } catch (InterruptedException e) {
                            e.printStackTrace();
                        }
                    }
                })
                .collect(EvolutionResult.toBestPhenotype());

        // Mark as finished
        if (!headless) {
            visualizationFrame.markFinished();
        }

        PackingResult finalResult = decoder.decode(best.genotype());
        
        if (headless) {
            // Output JSON for headless mode
            String jsonOutput = JsonOutputGenerator.generateJsonOutput(finalResult, best.fitness());
            System.out.println(jsonOutput);
        } else {
            // Output human-readable format for GUI mode
            System.out.println("\n" + "=".repeat(80));
            System.out.println("OPTIMIZATION FINISHED!");
            System.out.println("=".repeat(80));
            System.out.println("Best Fitness: " + String.format("%.2f", best.fitness()));

            System.out.println("\nFinal Results:");
            System.out.println("  Packed Value: $" + String.format("%.2f", finalResult.totalPackedValue));
            System.out.println("  Unplaced Items: " + finalResult.unplacedItems.size());
            System.out.println("\nBin Details:");
            for (Bin bin : finalResult.bins) {
                System.out.printf("  Bin %d: %d items, %.1f%% utilization%n",
                        bin.id, bin.placedItems.size(), bin.getUtilization() * 100);
            }
        }
    }
}

// ============================================================================
// Main Application
// ============================================================================

public class Code2 {
    public static void main(String[] args) {
        CommandLineParser parser = new CommandLineParser();
        
        if (parser.parse(args)) {
            // JSON input mode
            try {
                JsonInput jsonInput = JsonInputLoader.loadFromFile(parser.getInputFile());
                List<Item> items = JsonInputLoader.convertToItems(jsonInput.items);
                List<Bin> bins = JsonInputLoader.convertToBins(jsonInput.bins);
                
                BinPackingProblem problem = new BinPackingProblem(items, bins, parser.isHeadless());
                problem.solve();
            } catch (IOException e) {
                System.err.println("Error loading input file: " + e.getMessage());
                System.exit(1);
            }
        } else {
            // Default hardcoded mode
            List<Item> allItems = new ArrayList<>();
            int itemIdCounter = 0;

            // Rectangles
            for (int i = 0; i < 15; i++)
                allItems.add(new Item(itemIdCounter++, "Rectangle A",
                        new Dimensions(50, 50, ShapeType.RECTANGLE), 100));
            for (int i = 0; i < 25; i++)
                allItems.add(new Item(itemIdCounter++, "Rectangle B",
                        new Dimensions(35, 45, ShapeType.RECTANGLE), 150));
            for (int i = 0; i < 40; i++)
                allItems.add(new Item(itemIdCounter++, "Rectangle C",
                        new Dimensions(25, 30, ShapeType.RECTANGLE), 70));
            for (int i = 0; i < 60; i++)
                allItems.add(new Item(itemIdCounter++, "Rectangle D",
                        new Dimensions(30, 40, ShapeType.RECTANGLE), 300));

            // Triangles
            for (int i = 0; i < 30; i++)
                allItems.add(new Item(itemIdCounter++, "Triangle Small",
                        new Dimensions(30, 30, ShapeType.TRIANGLE), 120));
            for (int i = 0; i < 20; i++)
                allItems.add(new Item(itemIdCounter++, "Triangle Large",
                        new Dimensions(45, 45, ShapeType.TRIANGLE), 180));

            // Circles
            for (int i = 0; i < 25; i++)
                allItems.add(new Item(itemIdCounter++, "Circle Small",
                        new Dimensions(30, 30, ShapeType.CIRCLE), 90));
            for (int i = 0; i < 15; i++)
                allItems.add(new Item(itemIdCounter++, "Circle Medium",
                        new Dimensions(40, 40, ShapeType.CIRCLE), 200));

            // 4 Bins with different sizes
            List<Bin> bins = List.of(
                    new Bin(0, new Dimensions(220, 220, ShapeType.RECTANGLE)),
                    new Bin(1, new Dimensions(180, 200, ShapeType.RECTANGLE)),
                    new Bin(2, new Dimensions(200, 180, ShapeType.RECTANGLE)),
                    new Bin(3, new Dimensions(160, 160, ShapeType.RECTANGLE))
            );

            BinPackingProblem problem = new BinPackingProblem(allItems, bins);
            problem.solve();
        }
    }
}