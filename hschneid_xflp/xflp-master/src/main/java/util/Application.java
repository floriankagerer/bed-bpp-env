package util;

import xf.xflp.XFLP;
import xf.xflp.opt.XFLPOptType;
import xf.xflp.report.LPReport;
import xf.xflp.report.StringReportWriter;

import org.json.simple.JSONObject;
import org.json.simple.parser.*;

import java.io.BufferedWriter;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.io.PrintWriter;
import java.util.Iterator;
import java.util.Map;

/**
 *
 *
 * @author kafo
 *
 */
public class Application {
	public static void main(String[] args) {
		String srcfile;
		if (args.length==0){
			srcfile = "../../example_data/benchmark_data/bed-bpp_v1.json";			
		} else {
			srcfile = args[0];
		}
		
		System.out.println("used the source file: " + srcfile);
		
		try {
			int MAX_CONTAINER_HEIGHT = 2000;
			// is needed in gramm since container allows only ints as weight
			int MAX_CONTAINER_WEIGHT_KG = 1500;
			// load the order from json file
			JSONParser jsonParser = new JSONParser();
			JSONObject benchmarkData = (JSONObject) jsonParser.parse(new FileReader(srcfile));
			Iterator<Map.Entry> orderidValuesDictIterator = benchmarkData.entrySet().iterator();
			
			String orderID = "";

			// iterate over all orders
			while (orderidValuesDictIterator.hasNext()){
				XFLP xflp = new XFLP();
				xflp.setTypeOfOptimization(XFLPOptType.SINGLE_CONTAINER_OPTIMIZER);

				Map.Entry idValuePair = orderidValuesDictIterator.next();

				orderID = idValuePair.getKey().toString();

				JSONObject orderValues = (JSONObject) idValuePair.getValue();

				int CONTAINER_LENGTH = 0;
				int CONTAINER_WIDTH = 0;
				
				// use the information about the order's properties
				JSONObject order_properties = (JSONObject) orderValues.get("properties");
				String goal = order_properties.get("target").toString();
				// System.out.println("goal = " + goal);
				if (goal.equals("euro-pallet")) {
					// swap length and width for correct results
					CONTAINER_LENGTH = 800;
					CONTAINER_WIDTH = 1200;
				} else if (goal.equals("rollcontainer")) {
					// swap length and width for correct results
					CONTAINER_LENGTH = 700;
					CONTAINER_WIDTH = 800;

				} else {
					System.out.println("Target IS UNKNOWN!!!");
				}
				xflp.addContainer().setLength(CONTAINER_LENGTH).setWidth(CONTAINER_WIDTH).setHeight(MAX_CONTAINER_HEIGHT).setMaxWeight(MAX_CONTAINER_WEIGHT_KG);


				// add the items of the item_sequence
				Iterator<Map.Entry> orderDictIterator = orderValues.entrySet().iterator();


				
				while (orderDictIterator.hasNext()){
					Map.Entry pair = orderDictIterator.next();
					// System.out.println("input | " + pair.getKey()+ " : " + pair.getValue());
		
					if (pair.getKey().equals("item_sequence")) {
						JSONObject items = (JSONObject) pair.getValue();
						Iterator<Map.Entry> itemsIterator = items.entrySet().iterator();
							
						// add all items for stacking
						while (itemsIterator.hasNext()) {
							Map.Entry itemProperties = itemsIterator.next();
							JSONObject props = (JSONObject) itemProperties.getValue();
							Integer length = ((Number) props.get("length/mm")).intValue();
							Integer width = ((Number) props.get("width/mm")).intValue();
							Integer height = ((Number) props.get("height/mm")).intValue();
							float weightKG = ((Number) props.get("weight/kg")).floatValue();
							String description = props.get("article").toString();
							
							xflp.addItem().setExternID(description).setLength(length).setWidth(width).setHeight(height).setWeight((float) weightKG);
						}
					}
				}
				// System.out.println("Execute the loading plan for order " + orderID);
				xflp.executeLoadPlanning();
				// System.out.println("finished executing " + orderID);

				LPReport report = xflp.getReport();
				
				StringReportWriter str_report_writer = new StringReportWriter();
				String placements = str_report_writer.write(report);
				// System.out.println(placements);
				System.out.println("Order " + orderID + ": nr of not loaded packages = " + report.getSummary().getNbrOfNotLoadedPackages());

				BufferedWriter writer2 = new BufferedWriter(new FileWriter("java_output.txt", true));
				PrintWriter writer = new PrintWriter(writer2);
				writer.append("====================\norder id:" + orderID + "\nnot placed items=" + report.getSummary().getNbrOfNotLoadedPackages() + "\n" + placements);
				writer.close();
			}
			
			BufferedWriter writer2 = new BufferedWriter(new FileWriter("java_output.txt", true));
			PrintWriter writer = new PrintWriter(writer2);
			writer.append("====================\n");
			writer.close();			
		} catch (Exception e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
			System.out.println(e);
		} 
	}
}
