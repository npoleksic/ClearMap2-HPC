function cellPlotter % APP FOR PLOTTING CELL COUNT RESULTS
    s = load('region_data.mat');
    region_data = [s.region_data{:}];
    for j = 1:length(region_data)
        region_data(j).Name = string(region_data(j).Name);
    end

    fig = uifigure;
    fig.Position = [50 50 1400 700];
    tree = uitree(fig, 'tree', 'Position', [20 70 300 600]);
    plotContainer = uiaxes(fig, 'Position', [350 80 1000 600]);
    plotContainer.Title.String = "Density of c-Fos-Expressing Cells by Region";
    plotContainer.YLabel.String = "# of Cells per mm^3";
    plotContainer.YGrid = 'on';
    plotContainer.YScale = 'log';
    saveBtn = uibutton(fig, 'Text', 'SAVE AS PNG', 'Position', [600 20 100 40]);
    clearBtn = uibutton(fig, 'Text', 'CLEAR', 'Position', [800 20 100 40]);
    backBtn = uibutton(fig, 'Text', 'BACK', 'Position', [1000 20 100 40]);
    uilabel(fig, 'Text', 'DOUBLE-CLICK ON A REGION TO ADD IT TO THE PLOT', 'Position', [15 670 320 30]);

    saveBtn.ButtonPushedFcn = @SavePlot;
    clearBtn.ButtonPushedFcn = @ClearPlot;
    backBtn.ButtonPushedFcn = @RemovePrevious;

    tree.DoubleClickedFcn = @DoubleClick;

    brain = uitreenode(tree, 'Text', 'Brain', 'NodeData', []);
    populateNodes(brain, region_data)
    
    nameList = categorical([]);
    dataList = [];

    function populateNodes(brain, region_data)
        for i = 1:length(region_data)
            if region_data(i).ParentID == 997
                newNode = uitreenode(brain, "Text", region_data(i).Name, "NodeData", region_data(i).Density);
                addNode(newNode, region_data(i).ID, region_data);
            end
        end
    end

    function addNode(parentNode, parentID, region_data)
        index = find([region_data.ID] == parentID, 1);
        if isempty(index)
            disp("ID: ", parentID)
            error("Could not find region for ID")
        end
        region = region_data(index);
        if ~isempty(region.Children)
            for i = 1:length(region.Children)
                index = find(strcmp([region_data.Name], region.Children{i}), 1);
                if isempty(index)
                    continue;
                end
                name = region_data(index).Name;
                count = region_data(index).Density;
                ID = region_data(index).ID;
                newNode = uitreenode(parentNode, "Text", name, "NodeData", count);
                addNode(newNode, ID, region_data);
            end
        end
    end

    function DoubleClick(~, event)
        node = event.InteractionInformation.Node;
        name = cellstr(node.Text);
        if name ~= "Brain" && ~ismember(categorical(name), nameList)
            data = node.NodeData;
            if data>0
                nameList = [nameList name];
                dataList = [dataList data];
                nameList = categorical(nameList);
                barplt = bar(plotContainer, nameList, dataList);
                barplt.FaceColor = 'flat';
                barplt.CData = parula(size(barplt.CData,1));
                plotContainer.YLim = [(min(dataList)/10) (max(dataList)*1.5)];
            end
        end
    end
    
    function SavePlot(~, ~)
        timestamp = string(datetime("now", 'Format','MM-dd-yy_HHmmss'));
        exportName = strcat("BrainRegionPlot_", timestamp, ".png");
        exportgraphics(plotContainer, exportName)
    end

    function ClearPlot(~, ~)
        nameList = categorical([]);
        dataList = [];    
        plotContainer.XAxis.Categories = nameList;
        bar(plotContainer, nameList, dataList);
    end

    function RemovePrevious(~, ~)
        if ~isempty(nameList)
            nameList(end) = [];
            dataList(end) = [];
            nameList = removecats(nameList);
            plotContainer.XAxis.Categories = nameList;
            barplt = bar(plotContainer, nameList, dataList);
            if ~isempty(nameList)
                barplt.FaceColor = 'flat';
                barplt.CData = parula(size(barplt.CData,1)); 
            end
        end
    end
end

