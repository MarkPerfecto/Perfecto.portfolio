package finalsOOP;
import java.awt.*;
import java.awt.event.*;
import javax.swing.*;
import javax.swing.border.*;
import java.awt.geom.*;
import java.awt.image.BufferedImage; // Add this import for BufferedImage
import javax.imageio.ImageIO; // Add this import for ImageIO
import java.io.File;
import java.io.IOException;
import java.net.URL;
import java.util.ArrayList;
import java.util.List;
import java.util.Random;


public class CharacterCreator extends JFrame {

    private static final long serialVersionUID = 1L;
    private JPanel contentPane;
    private ImagePanel imagePanel;
    private JButton nextBaseButton;
    private JButton prevBaseButton;
    private JButton nextFaceButton;
    private JButton prevFaceButton;
    private JButton nextHairButton;
    private JButton prevHairButton;
    private JButton randomizeButton;
    private JButton resetButton;
    private JButton saveButton; // Button for saving the image
    private JCheckBox circlePreviewCheckBox;
    private JLabel baseLabel;
    private JLabel faceLabel;
    private JLabel hairLabel;
    private JLabel menuLabel;
    private JPanel controlPanel;
    private JPanel topPanel;

    private BufferedImage[] baseImages;
    private BufferedImage[] faceImages;
    private BufferedImage[] hairImages;
    private int baseIndex;
    private int faceIndex;
    private int hairIndex;

    private final Random random = new Random();

    public static void main(String[] args) {
        EventQueue.invokeLater(new Runnable() {
            public void run() {
                try {
                    CharacterCreator frame = new CharacterCreator();
                    frame.setVisible(true);
                } catch (Exception e) {
                    e.printStackTrace();
                }
            }
        });
    }

    public CharacterCreator() {
        setTitle("Anigen");
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setBounds(100, 100, 780, 520);
        contentPane = new JPanel();
        contentPane.setBorder(new EmptyBorder(5, 5, 5, 5));
        contentPane.setLayout(new BorderLayout());
        setContentPane(contentPane);

        try {
            URL iconUrl = getClass().getResource("logo.png");
            if (iconUrl != null) {
                BufferedImage icon = ImageIO.read(iconUrl);
                if (icon != null) {
                    setIconImage(icon);
                }
            }
        } catch (IOException e) {
        }

        loadAllAssets();
        baseIndex = 0;
        faceIndex = 0;
        hairIndex = 0;

        imagePanel = new ImagePanel();
        imagePanel.setPreferredSize(new Dimension(420, 420)); // Set the preferred size of the image panel
        contentPane.add(imagePanel, BorderLayout.CENTER);

        topPanel = new JPanel(new FlowLayout(FlowLayout.CENTER));
        topPanel.setBackground(Color.WHITE);
        contentPane.add(topPanel, BorderLayout.NORTH);

        menuLabel = new JLabel("Anigen");
        menuLabel.setFont(new Font("Arial", Font.BOLD, 16));
        topPanel.add(menuLabel);

        controlPanel = new JPanel();
        controlPanel.setLayout(new BoxLayout(controlPanel, BoxLayout.Y_AXIS)); // Change to vertical layout
        controlPanel.setBackground(Color.WHITE);
        contentPane.add(controlPanel, BorderLayout.EAST);

        controlPanel.setBorder(new EmptyBorder(10, 10, 10, 10));

        JPanel basePanel = new JPanel();
        basePanel.setBackground(Color.WHITE);
        basePanel.setLayout(new BoxLayout(basePanel, BoxLayout.Y_AXIS));

        JLabel baseTitle = new JLabel("Base");
        baseTitle.setAlignmentX(Component.CENTER_ALIGNMENT);
        basePanel.add(baseTitle);

        JPanel baseButtonsPanel = new JPanel(new FlowLayout(FlowLayout.CENTER, 6, 0));
        baseButtonsPanel.setBackground(Color.WHITE);
        prevBaseButton = new JButton("<");
        nextBaseButton = new JButton(">");
        baseButtonsPanel.add(prevBaseButton);
        baseButtonsPanel.add(nextBaseButton);
        basePanel.add(baseButtonsPanel);

        baseLabel = new JLabel();
        baseLabel.setAlignmentX(Component.CENTER_ALIGNMENT);
        basePanel.add(baseLabel);

        JPanel facePanel = new JPanel();
        facePanel.setBackground(Color.WHITE);
        facePanel.setLayout(new BoxLayout(facePanel, BoxLayout.Y_AXIS));

        JLabel faceTitle = new JLabel("Face");
        faceTitle.setAlignmentX(Component.CENTER_ALIGNMENT);
        facePanel.add(faceTitle);

        JPanel faceButtonsPanel = new JPanel(new FlowLayout(FlowLayout.CENTER, 6, 0));
        faceButtonsPanel.setBackground(Color.WHITE);
        prevFaceButton = new JButton("<");
        nextFaceButton = new JButton(">");
        faceButtonsPanel.add(prevFaceButton);
        faceButtonsPanel.add(nextFaceButton);
        facePanel.add(faceButtonsPanel);

        faceLabel = new JLabel();
        faceLabel.setAlignmentX(Component.CENTER_ALIGNMENT);
        facePanel.add(faceLabel);

        JPanel hairPanel = new JPanel();
        hairPanel.setBackground(Color.WHITE);
        hairPanel.setLayout(new BoxLayout(hairPanel, BoxLayout.Y_AXIS));

        JLabel hairTitle = new JLabel("Hair");
        hairTitle.setAlignmentX(Component.CENTER_ALIGNMENT);
        hairPanel.add(hairTitle);

        JPanel hairButtonsPanel = new JPanel(new FlowLayout(FlowLayout.CENTER, 6, 0));
        hairButtonsPanel.setBackground(Color.WHITE);
        prevHairButton = new JButton("<");
        nextHairButton = new JButton(">");
        hairButtonsPanel.add(prevHairButton);
        hairButtonsPanel.add(nextHairButton);
        hairPanel.add(hairButtonsPanel);

        hairLabel = new JLabel();
        hairLabel.setAlignmentX(Component.CENTER_ALIGNMENT);
        hairPanel.add(hairLabel);

        circlePreviewCheckBox = new JCheckBox("Circle preview");
        circlePreviewCheckBox.setBackground(Color.WHITE);
        circlePreviewCheckBox.setSelected(true);

        JPanel actionsPanel = new JPanel(new FlowLayout(FlowLayout.CENTER, 6, 0));
        actionsPanel.setBackground(Color.WHITE);
        randomizeButton = new JButton("Random");
        resetButton = new JButton("Reset");
        actionsPanel.add(randomizeButton);
        actionsPanel.add(resetButton);

        saveButton = new JButton("Save as PNG");

        controlPanel.add(basePanel);
        controlPanel.add(Box.createVerticalStrut(10));
        controlPanel.add(facePanel);
        controlPanel.add(Box.createVerticalStrut(10));
        controlPanel.add(hairPanel);
        controlPanel.add(Box.createVerticalStrut(10));
        controlPanel.add(circlePreviewCheckBox);
        controlPanel.add(Box.createVerticalStrut(10));
        controlPanel.add(actionsPanel);
        controlPanel.add(Box.createVerticalStrut(10));
        controlPanel.add(saveButton);

        prevBaseButton.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent e) {
                baseIndex = (baseIndex - 1 + baseImages.length) % baseImages.length;
                updateLabels();
                imagePanel.repaint();
            }
        });
        nextBaseButton.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent e) {
                baseIndex = (baseIndex + 1) % baseImages.length;
                updateLabels();
                imagePanel.repaint();
            }
        });
        prevFaceButton.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent e) {
                faceIndex = (faceIndex - 1 + faceImages.length) % faceImages.length;
                updateLabels();
                imagePanel.repaint();
            }
        });
        nextFaceButton.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent e) {
                faceIndex = (faceIndex + 1) % faceImages.length;
                updateLabels();
                imagePanel.repaint();
            }
        });
        prevHairButton.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent e) {
                hairIndex = (hairIndex - 1 + hairImages.length) % hairImages.length;
                updateLabels();
                imagePanel.repaint();
            }
        });
        nextHairButton.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent e) {
                hairIndex = (hairIndex + 1) % hairImages.length;
                updateLabels();
                imagePanel.repaint();
            }
        });
        circlePreviewCheckBox.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent e) {
                imagePanel.repaint();
            }
        });
        randomizeButton.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent e) {
                baseIndex = random.nextInt(baseImages.length);
                faceIndex = random.nextInt(faceImages.length);
                hairIndex = random.nextInt(hairImages.length);
                updateLabels();
                imagePanel.repaint();
            }
        });
        resetButton.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent e) {
                baseIndex = 0;
                faceIndex = 0;
                hairIndex = 0;
                updateLabels();
                imagePanel.repaint();
            }
        });
        saveButton.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent e) {
                saveImageAsPNG();
            }
        });

        updateLabels();
    }

    private class ImagePanel extends JPanel {
        @Override
        protected void paintComponent(Graphics g) {
            super.paintComponent(g);
            Graphics2D g2d = (Graphics2D) g.create();
            g2d.setRenderingHint(RenderingHints.KEY_INTERPOLATION, RenderingHints.VALUE_INTERPOLATION_BILINEAR);
            g2d.setRenderingHint(RenderingHints.KEY_RENDERING, RenderingHints.VALUE_RENDER_QUALITY);
            g2d.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);

            int diameter = Math.min(getWidth(), getHeight());
            int clipX = (getWidth() - diameter) / 2;
            int clipY = (getHeight() - diameter) / 2;

            if (circlePreviewCheckBox != null && circlePreviewCheckBox.isSelected()) {
                Ellipse2D.Double circle = new Ellipse2D.Double(clipX, clipY, diameter, diameter);
                g2d.setClip(circle);
            }

            drawLayeredCharacter(g2d, getWidth(), getHeight());
            g2d.dispose();
        }
    }

    private void updateLabels() {
        if (baseLabel != null) {
            baseLabel.setText("Base " + (baseIndex + 1) + " / " + baseImages.length);
        }
        if (faceLabel != null) {
            faceLabel.setText("Face " + (faceIndex + 1) + " / " + faceImages.length);
        }
        if (hairLabel != null) {
            hairLabel.setText("Hair " + (hairIndex + 1) + " / " + hairImages.length);
        }
    }

    // Method to save the current image as a PNG file
    private void saveImageAsPNG() {
        try {
            int w = imagePanel.getWidth();
            int h = imagePanel.getHeight();
            int diameter = Math.min(w, h);
            int x = (w - diameter) / 2;
            int y = (h - diameter) / 2;

            BufferedImage image = new BufferedImage(w, h, BufferedImage.TYPE_INT_ARGB);
            Graphics2D g2d = image.createGraphics();
            g2d.setRenderingHint(RenderingHints.KEY_INTERPOLATION, RenderingHints.VALUE_INTERPOLATION_BILINEAR);
            g2d.setRenderingHint(RenderingHints.KEY_RENDERING, RenderingHints.VALUE_RENDER_QUALITY);
            g2d.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);

            if (circlePreviewCheckBox != null && circlePreviewCheckBox.isSelected()) {
                Shape clip = new Ellipse2D.Double(x, y, diameter, diameter);
                g2d.setClip(clip);
            }

            drawLayeredCharacter(g2d, w, h);
            g2d.dispose();

            BufferedImage output = image;
            if (circlePreviewCheckBox != null && circlePreviewCheckBox.isSelected()) {
                output = image.getSubimage(x, y, diameter, diameter);
            }

            JFileChooser fileChooser = new JFileChooser();
            fileChooser.setDialogTitle("Save Image");
            fileChooser.setSelectedFile(new File("anigen.png"));
            int userSelection = fileChooser.showSaveDialog(this);

            if (userSelection == JFileChooser.APPROVE_OPTION) {
                File fileToSave = fileChooser.getSelectedFile();
                ImageIO.write(output, "png", fileToSave);
                JOptionPane.showMessageDialog(this, "Image saved successfully!");
            }
        } catch (IOException ex) {
            ex.printStackTrace();
            JOptionPane.showMessageDialog(this, "Error saving image: " + ex.getMessage(), "Error", JOptionPane.ERROR_MESSAGE);
        }
    }

    private void drawLayeredCharacter(Graphics2D g2d, int panelWidth, int panelHeight) {
        BufferedImage base = (baseImages != null && baseImages.length > 0) ? baseImages[baseIndex] : null;
        BufferedImage face = (faceImages != null && faceImages.length > 0) ? faceImages[faceIndex] : null;
        BufferedImage hair = (hairImages != null && hairImages.length > 0) ? hairImages[hairIndex] : null;

        BufferedImage reference = base;
        if (reference == null) {
            reference = face;
        }
        if (reference == null) {
            reference = hair;
        }
        if (reference == null) {
            return;
        }

        int refW = reference.getWidth();
        int refH = reference.getHeight();
        double scale = Math.min((double) panelWidth / refW, (double) panelHeight / refH);
        int drawW = (int) Math.round(refW * scale);
        int drawH = (int) Math.round(refH * scale);
        int x = (panelWidth - drawW) / 2;
        int y = (panelHeight - drawH) / 2;

        if (base != null) {
            g2d.drawImage(base, x, y, drawW, drawH, null);
        }
        if (face != null) {
            g2d.drawImage(face, x, y, drawW, drawH, null);
        }
        if (hair != null) {
            g2d.drawImage(hair, x, y, drawW, drawH, null);
        }
    }

    private void loadAllAssets() {
        File patchFolder = findPatcherFolder();

        List<BufferedImage> bases = new ArrayList<BufferedImage>();
        List<BufferedImage> faces = new ArrayList<BufferedImage>();
        List<BufferedImage> hairs = new ArrayList<BufferedImage>();

        addSequentialResourceImages(bases, "p", 1, 50, "png");
        addSequentialResourceImages(faces, "face", 1, 50, "png");
        addSequentialResourceImages(hairs, "hair", 1, 50, "png");

        if (patchFolder != null) {
            if (bases.isEmpty()) {
                addSequentialFileImages(bases, patchFolder, "p", 1, 50, "png");
            }
            if (faces.isEmpty()) {
                addSequentialFileImages(faces, patchFolder, "face", 1, 50, "png");
            }
            if (hairs.isEmpty()) {
                addSequentialFileImages(hairs, patchFolder, "hair", 1, 50, "png");
            }
        }

        if (bases.isEmpty()) {
            addSequentialResourceImages(bases, "girl", 1, 4, "png");
        }
        if (faces.isEmpty()) {
            faces.add(createTransparentFallback(bases));
        }
        if (hairs.isEmpty()) {
            hairs.add(createTransparentFallback(bases));
        }

        baseImages = bases.toArray(new BufferedImage[0]);
        faceImages = faces.toArray(new BufferedImage[0]);
        hairImages = hairs.toArray(new BufferedImage[0]);
    }

    private File findPatcherFolder() {
        try {
            File current = new File(System.getProperty("user.dir"));
            File sibling = new File(current.getParentFile(), "character creator patcher");
            if (sibling.exists() && sibling.isDirectory()) {
                return sibling;
            }
            File local = new File(current, "character creator patcher");
            if (local.exists() && local.isDirectory()) {
                return local;
            }
        } catch (Exception e) {
        }
        return null;
    }

    private void addSequentialFileImages(List<BufferedImage> out, File folder, String prefix, int start, int max, String ext) {
        for (int i = start; i <= max; i++) {
            File f = new File(folder, prefix + i + "." + ext);
            if (!f.exists()) {
                if (i == start) {
                    continue;
                }
                break;
            }
            try {
                BufferedImage img = ImageIO.read(f);
                if (img != null) {
                    out.add(img);
                }
            } catch (IOException e) {
            }
        }
    }

    private void addSequentialResourceImages(List<BufferedImage> out, String prefix, int start, int max, String ext) {
        for (int i = start; i <= max; i++) {
            String name = prefix + i + "." + ext;
            URL url = getClass().getResource(name);
            if (url == null) {
                break;
            }
            try {
                BufferedImage img = ImageIO.read(url);
                if (img != null) {
                    out.add(img);
                }
            } catch (IOException e) {
            }
        }
    }

    private BufferedImage createTransparentFallback(List<BufferedImage> bases) {
        int w = 512;
        int h = 512;
        if (bases != null && !bases.isEmpty() && bases.get(0) != null) {
            w = bases.get(0).getWidth();
            h = bases.get(0).getHeight();
        }
        return new BufferedImage(w, h, BufferedImage.TYPE_INT_ARGB);
    }





}
